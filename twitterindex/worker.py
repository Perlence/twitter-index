from gevent import monkey
monkey.patch_all(thread=False, select=False)

from functools import partial

import arrow
import twitter
from gevent import spawn, sleep, joinall
from logbook import Logger, StderrHandler
from termcolor import colored

from . import config
from .models import TweetIndex


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

INTERVAL = 60  # 15 calls in 15 minutes


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


def load_to(method, option):
    max_id = getattr(config, option)
    params = {'count': 200}
    if max_id is not None:
        params['max_id'] = int(max_id) - 1
    span = load_tweets(method, params)
    if span is not None:
        min_id, __ = span
    else:
        min_id = '0'
    setattr(config, option, min_id)
    config.save()


def load_since(method, option, history_option):
    since_id = getattr(config, option)
    params = {'count': 200}
    if since_id is not None:
        params['since_id'] = since_id
    span = load_tweets(method, params)
    if span is not None:
        min_id, max_id = span
        setattr(config, option, max_id)
        if getattr(config, history_option) is None:
            setattr(config, history_option, min_id)
        config.save()


def load_home_timeline_history():
    load_to(api.statuses.home_timeline,
            'HISTORY_HOME_TIMELINE_MAX_ID')


def load_favorites_history():
    load_to(api.favorites.list,
            'HISTORY_FAVORITES_MAX_ID')


def load_home_timeline():
    load_since(api.statuses.home_timeline,
               'HOME_TIMELINE_LAST_ID', 'HISTORY_HOME_TIMELINE_MAX_ID')


def load_favorites():
    load_since(api.favorites.list,
               'FAVORITES_LAST_ID', 'HISTORY_FAVORITES_MAX_ID')


def main():
    @spawn
    def home_timeline():
        while True:
            spawn(load_home_timeline)
            sleep(INTERVAL)
            if config.HISTORY_HOME_TIMELINE_MAX_ID != '0':
                spawn(load_home_timeline_history)
                sleep(INTERVAL)

    @spawn
    def favorites():
        while True:
            spawn(load_favorites)
            sleep(INTERVAL)
            if config.HISTORY_FAVORITES_MAX_ID != '0':
                spawn(load_favorites_history)
                sleep(INTERVAL)

    joinall([home_timeline, favorites])


if __name__ == '__main__':
    main()
