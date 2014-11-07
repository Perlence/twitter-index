import os
from datetime import datetime

from mongoengine import (Document, EmbeddedDocument,
                         IntField, BooleanField, FloatField, StringField,
                         DateTimeField, ListField, DictField,
                         EmbeddedDocumentField)
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, NUMERIC, TEXT, BOOLEAN, DATETIME

from . import config


class Contributor(EmbeddedDocument):
    id = IntField()
    id_str = StringField()
    screen_name = StringField()


class Coordinates(EmbeddedDocument):
    coordinates = ListField(FloatField())
    type = StringField()


class Hashtag(EmbeddedDocument):
    indices = ListField(IntField())
    text = StringField()


class Size(EmbeddedDocument):
    h = IntField()
    w = IntField()
    resize = StringField()


class SizesSizes(EmbeddedDocument):
    thumb = EmbeddedDocumentField(Size)
    large = EmbeddedDocumentField(Size)
    medium = EmbeddedDocumentField(Size)
    small = EmbeddedDocumentField(Size)


class Sizes(EmbeddedDocument):
    id = IntField()
    id_str = StringField()
    display_url = StringField()
    expanded_url = StringField()
    indices = ListField(IntField())
    media_url = StringField()
    media_url_https = StringField()
    sizes = EmbeddedDocumentField(SizesSizes)
    source_status_id = StringField()
    source_status_id_str = StringField()
    type = StringField()
    url = StringField()


class Media(EmbeddedDocument):
    id = IntField()
    id_str = StringField()
    display_url = StringField()
    expanded_url = StringField()
    indices = ListField(IntField())
    media_url = StringField()
    media_url_https = StringField()
    sizes = EmbeddedDocumentField(Sizes)
    source_status_id = IntField()
    source_status_id_str = StringField()
    type = StringField()
    url = StringField()


class URL(EmbeddedDocument):
    display_url = StringField()
    expanded_url = StringField()
    indices = ListField(IntField())
    url = StringField()


class UserMention(EmbeddedDocument):
    id = IntField()
    id_str = StringField()
    indices = ListField(IntField())
    name = StringField()
    screen_name = StringField()


class Entities(EmbeddedDocument):
    hashtags = ListField(EmbeddedDocumentField(Hashtag))
    media = ListField(EmbeddedDocumentField(Media))
    urls = ListField(EmbeddedDocumentField(URL))
    user_mentions = ListField(EmbeddedDocumentField(UserMention))


class Attributes(EmbeddedDocument):
    street_address = StringField()
    locality = StringField()
    region = StringField()
    iso3 = StringField()
    postal_code = StringField()
    phone = StringField()
    twitter = StringField()
    url = StringField()
    app_id = StringField(db_field='app:id')


class BoundingBox(EmbeddedDocument):
    coordinates = ListField(ListField(ListField(FloatField())))
    type = StringField()


class Place(EmbeddedDocument):
    id = StringField()
    attributes = EmbeddedDocumentField(Attributes)
    bounding_box = EmbeddedDocumentField(BoundingBox)
    country = StringField()
    country_code = StringField()
    full_name = StringField()
    name = StringField()
    place_type = StringField()
    url = StringField()


class User(EmbeddedDocument):
    id = IntField()
    id_str = StringField()
    contributors_enabled = BooleanField()
    created_at = datetime
    default_profile = BooleanField()
    default_profile_image = BooleanField()
    description = StringField()
    entities = EmbeddedDocumentField(Entities)
    favourites_count = IntField()
    follow_request_sent = BooleanField()
    followers_count = IntField()
    following = BooleanField()
    friends_count = IntField()
    geo_enabled = BooleanField()
    is_translation_enabled = BooleanField()
    is_translator = BooleanField()
    lang = StringField()
    listed_count = IntField()
    location = StringField()
    name = StringField()
    notifications = BooleanField()
    profile_background_color = StringField()
    profile_background_image_url = StringField()
    profile_background_image_url_https = StringField()
    profile_background_tile = BooleanField()
    profile_banner_url = StringField()
    profile_image_url = StringField()
    profile_image_url_https = StringField()
    profile_link_color = StringField()
    profile_sidebar_border_color = StringField()
    profile_sidebar_fill_color = StringField()
    profile_text_color = StringField()
    profile_use_background_image = BooleanField()
    protected = BooleanField()
    screen_name = StringField()
    show_all_inline_media = BooleanField()
    statuses_count = IntField()
    time_zone = StringField()
    url = StringField()
    utc_offset = IntField()
    verified = BooleanField()
    withheld_in_countries = StringField()
    withheld_scope = StringField()


class Tweet(Document):
    id = IntField(primary_key=True)
    id_str = StringField()
    annotations = DictField()
    contributors = ListField(EmbeddedDocumentField(Contributor))
    coordinates = EmbeddedDocumentField(Coordinates)
    created_at = DateTimeField()
    current_user_retweet = EmbeddedDocumentField('Tweet')
    entities = EmbeddedDocumentField(Entities)
    favorite_count = IntField()
    favorited = BooleanField()
    filter_level = StringField()
    geo = DictField()
    in_reply_to_screen_name = StringField()
    in_reply_to_status_id = IntField()
    in_reply_to_status_id_str = StringField()
    in_reply_to_user_id = IntField()
    in_reply_to_user_id_str = StringField()
    lang = StringField()
    place = EmbeddedDocumentField(Place)
    possibly_sensitive = BooleanField()
    scopes = DictField()
    retweet_count = IntField()
    retweeted = BooleanField()
    retweeted_status = EmbeddedDocumentField('Tweet')
    source = StringField()
    text = StringField()
    truncated = BooleanField()
    user = EmbeddedDocumentField(User)
    withheld_copyright = BooleanField()
    withheld_in_countries = ListField(StringField())
    withheld_scope = StringField()

    def add_to_index(self, writer):
        indexed_fields = TweetSchema.names()
        doc = {}
        for field in indexed_fields:
            if field == 'from':
                value = self.user.screen_name
            else:
                value = getattr(self, field)
            doc[field] = value
        writer.add_document(**doc)


TweetSchema = Schema(**{
    'id': NUMERIC(bits=64, signed=False, stored=True),
    'created_at': DATETIME(),
    'favorited': BOOLEAN(),
    'retweeted': BOOLEAN(),
    'text': TEXT(),
    'from': TEXT(),
})

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
