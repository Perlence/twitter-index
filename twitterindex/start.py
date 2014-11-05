import arrow
import twitter

from . import config
from .models import TweetIndex


oauth = twitter.OAuth(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET,
                      config.CONSUMER_KEY, config.CONSUMER_SECRET)
api = twitter.Twitter(auth=oauth)


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


# def favorites():
#     statuses = api.statuses.home_timeline(exclude_replies=False, count=200)
#     statuses = api.favorites.list()

statuses = api.favorites.list()
store(statuses)
