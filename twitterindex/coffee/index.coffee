$ ->
  Tweet = Backbone.Model.extend
    defaults: ->
      created_at: new Date()
      text: ''
      user:
        name: 'User Name'


  Query = Backbone.Model.extend
    urlRoot: '/query'

    defaults: ->
      tweets: []

    initialize: ->
      this.listenTo(this, 'change:tweets', this.populateResults)

    populateResults: ->
      tweets.reset(this.get('tweets').map (tweet) -> new Tweet(tweet))


  TweetList = Backbone.Collection.extend
    model: Tweet


  TweetView = Backbone.View.extend
    template: _.template($('#tweet').html())

    initialize: ->
      this.listenTo(this.model, 'destroy', this.remove)

    render: ->
      this.$el.html(this.template(this.model.toJSON()))
      return this


  TwitterIndexApp = Backbone.View.extend
    el: $('#twitter-index-app')

    events:
      'click #submit': 'search'
      'keypress #input': 'searchOnEnter'

    initialize: ->
      this.$input = this.$('#input')

      this.listenTo(tweets, 'reset', this.addAll)

    search: ->
      this.model.set(id: this.$input.val())
      this.model.fetch()

    searchOnEnter: (e) ->
      return unless e.keyCode == 13
      return unless this.$input.val()
      this.search()

    addAll: (models, {previousModels})->
      previousModels.forEach (tweet) ->
        tweet.destroy()
      tweets.each (tweet) =>
        tweetView = new TweetView(model: tweet)
        this.$('#search-results').append(tweetView.render().el)

  tweets = new TweetList()
  query = new Query()
  app = new TwitterIndexApp(model: query)
