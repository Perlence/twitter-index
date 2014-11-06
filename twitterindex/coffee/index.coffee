$ ->
  Tweet = Backbone.Model.extend
    defaults: ->
      created_at: new Date()
      favorite_count: 0
      favorited: false
      retweet_count: 0
      retweeted: false
      text: ''
      truncated: false
      user: 'username'

  Tweets = Backbone.Collection.extend
    model: Tweet

  Query = Backbone.Model.extend
    urlRoot: '/query'
    defaults: ->
      tweets: new Tweets()
    parse: (response, options) ->
      result = _.clone(response)
      tweets = new Tweets()
      for tweet in response.tweets
        tweets.add(new Tweet(tweet))
      result.tweets = tweets
      return result
