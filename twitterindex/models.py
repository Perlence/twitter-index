import os

from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, ID, TEXT, BOOLEAN, NUMERIC, DATETIME

from . import config


TweetSchema = Schema(
    id_str=ID(stored=True),
    # 'coordinates': {
    #     'coordinates': (float, float),
    #     'type': unicode,
    # },
    created_at=DATETIME(stored=True),
    # 'current_user_retweet': DBRef,  # Tweet
    # 'entities': Entities,
    favorite_count=NUMERIC(stored=True),
    favorited=BOOLEAN(stored=True),
    # 'filter_level': unicode,
    # 'geo': dict,
    # 'lang': unicode,
    # 'place': {
    #     'id': unicode,
    #     'attributes': {
    #         'street_address': unicode,
    #         'locality': unicode,
    #         'region': unicode,
    #         'iso3': unicode,
    #         'postal_code': unicode,
    #         'phone': unicode,
    #         'twitter': unicode,
    #         'url': unicode,
    #         'app:id': unicode,
    #     },
    #     'bounding_box': {
    #         'coordinates': [[(float, float)]],
    #         'type': unicode,
    #     },
    #     'country': unicode,
    #     'country_code': unicode,
    #     'full_name': unicode,
    #     'name': unicode,
    #     'place_type': unicode,
    #     'url': unicode,
    # },
    # possibly_sensitive=BOOLEAN(stored=True),
    # 'scopes': dict,
    retweet_count=NUMERIC(stored=True),
    retweeted=BOOLEAN(stored=True),
    # 'source': unicode,
    text=TEXT(stored=True),
    truncated=BOOLEAN(stored=True),
    user=TEXT(stored=True),
    # 'withheld_copyright': bool,
    # 'withheld_in_countries': [unicode],
    # 'withheld_scope': unicode
    )

dirname = config.WHOOSH_INDEX_PATH
if dirname.startswith('./'):
    dirname = os.path.join(os.path.dirname(__file__), dirname[2:])
else:
    dirname = os.path.expanduser(dirname)

try:
    os.mkdir(dirname)
    TweetIndex = create_in(dirname, TweetSchema)
except OSError as e:
    # raise unless 'File exists'
    if e.errno != 17:
        raise
    TweetIndex = open_dir(dirname)
