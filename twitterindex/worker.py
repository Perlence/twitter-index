from gevent import monkey
monkey.patch_all(thread=False, select=False)

from collections import defaultdict
from functools import wraps, partial
from timeit import default_timer

import arrow
import twitter
from gevent import spawn, sleep
from gevent.pool import Pool
from logbook import Logger, StderrHandler
from schedule import Scheduler
from termcolor import colored

from . import config
from .models import TweetIndex


class GeventScheduler(Scheduler):
    def __init__(self, pool_size=None):
        super(GeventScheduler, self).__init__()
        self.pool = Pool(size=pool_size)

    def run_pending(self):
        runnable_jobs = (job for job in self.jobs if job.should_run)
        self.pool.map(self._run_job, sorted(runnable_jobs))


def throttle(interval=0):
    """Decorates a Greenlet function for throttling."""
    def decorate(func):
        blocked = defaultdict(bool)
        last_time = defaultdict(int)

        @wraps(func)
        def throttled_func(method, *args, **kwargs):
            uriparts = method.uriparts
            while True:
                sleep(0)
                if not blocked[uriparts]:
                    blocked[uriparts] = True
                    if interval:
                        last, current = (last_time[uriparts],
                                         default_timer())
                        elapsed = current - last
                        if elapsed < interval:
                            sleep(interval - elapsed)
                        last_time[uriparts] = default_timer()
                    blocked[uriparts] = False
                    return func(method, *args, **kwargs)
        return throttled_func
    return decorate


def logger_formatter(record, handler):
    return ("[{:%Y-%m-%d %H:%M:%S}] {}"
            .format(record.time,
                    colors[record.level](record.message)))


notset = partial(colored, color=None)
debug = partial(colored, color='green')
info = partial(colored, color='blue')
warn = partial(colored, color='yellow')
error = partial(colored, color='red')
critical = partial(colored, color='red', attrs=['bold'])
colors = [notset, debug, info, warn, error, critical]

logger = Logger('twitterindex.worker')
handler = StderrHandler()
handler.formatter = logger_formatter
logger.handlers.append(handler)

oauth = twitter.OAuth(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET,
                      config.CONSUMER_KEY, config.CONSUMER_SECRET)
api = twitter.Twitter(auth=oauth)

interval = 60  # 15 calls in 15 minutes


def store(statuses):
    writer = TweetIndex.writer()
    names = TweetIndex.schema.names()
    for status in statuses:
        filtered_status = {name: status.get(name) for name in names}
        created_at = arrow.get(filtered_status['created_at'],
                               'ddd MMM DD HH:mm:ss ZZ YYYY')
        filtered_status['created_at'] = created_at.datetime
        filtered_status['user'] = filtered_status['user']['screen_name']
        writer.add_document(**filtered_status)
    writer.commit()


@throttle(interval)
def load_tweets(method, params):
    logger.info('Getting tweets from {}: {}',
                '/'.join(method.uriparts), params)
    statuses = method(**params)
    logger.info('Got {} tweets from {}: {}',
                len(statuses), '/'.join(method.uriparts), params)
    if statuses:
        store(statuses)
        max_id = statuses[0]['id_str']
        min_id = statuses[-1]['id_str']
        return min_id, max_id


def load_home_timeline(since_id=None):
    since_id = since_id or config.HOME_TIMELINE_LAST_ID
    params = {'count': 200}
    if since_id is not None:
        params['since_id'] = since_id
    boundaries = load_tweets(api.statuses.home_timeline, params)
    if boundaries is not None:
        __, new_since_id = boundaries
        load_home_timeline(new_since_id)
        config.HOME_TIMELINE_LAST_ID = new_since_id
        config.save()


def load_favorites(since_id=None):
    since_id = since_id or config.FAVORITES_LAST_ID
    params = {'count': 200}
    if since_id is not None:
        params['since_id'] = since_id
    boundaries = load_tweets(api.favorites.list, params)
    if boundaries is not None:
        __, new_since_id = boundaries
        load_favorites(new_since_id)
        config.FAVORITES_LAST_ID = new_since_id
        config.save()


def load_home_timeline_history(max_id=None):
    max_id = max_id or config.HISTORY_HOME_TIMELINE_MAX_ID
    params = {'count': 200}
    if max_id is not None:
        params['max_id'] = int(max_id) - 1
    boundaries = load_tweets(api.statuses.home_timeline, params)
    if boundaries is not None:
        new_max_id, __ = boundaries
        config.HISTORY_HOME_TIMELINE_MAX_ID = new_max_id
        config.save()
        load_home_timeline_history(new_max_id)
    else:
        config.HISTORY_HOME_TIMELINE_MAX_ID = '0'
        config.save()


def load_favorites_history(max_id=None):
    max_id = max_id or config.HISTORY_FAVORITES_MAX_ID
    params = {'count': 200}
    if max_id is not None:
        params['max_id'] = int(max_id) - 1
    boundaries = load_tweets(api.favorites.list, params)
    if boundaries is not None:
        new_max_id, __ = boundaries
        config.HISTORY_FAVORITES_MAX_ID = new_max_id
        config.save()
        load_favorites_history(new_max_id)
    else:
        config.HISTORY_FAVORITES_MAX_ID = '0'
        config.save()


def main():
    if config.HISTORY_HOME_TIMELINE_MAX_ID != '0':
        spawn(load_home_timeline_history)
    if config.HISTORY_FAVORITES_MAX_ID != '0':
        spawn(load_favorites_history)

    scheduler = GeventScheduler()
    scheduler.every(1).minute.do(load_home_timeline)
    scheduler.every(1).minute.do(load_favorites)

    while True:
        scheduler.run_pending()
        sleep(1)


if __name__ == '__main__':
    main()
