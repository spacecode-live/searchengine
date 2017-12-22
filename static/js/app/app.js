// /static/js/app/app.js
window.App = Ember.Application.create();

App.UsernameValidatorService = Ember.Service.extend({

  validateUsername: function(username) {
    var store = this.get('store');
    return store.findRecord('user', username)
   }
});

Ember.Application.initializer({
  name: 'usernameValidator',
  after: 'store',
  initialize: function (app) {
    // Inject the Ember Data Store into our validator service
    app.inject('service:username-validator', 'store', 'store:main');

    // Inject the validator into all controllers and routes
    app.inject('controller', 'usernameValidator', 'service:username-validator');
    app.inject('route', 'usernameValidator', 'service:username-validator');
  }
});

App.Router = Ember.Router.extend({
  rootURL: '/j89pws9vn291/pa3/live'
});

App.Store = DS.Store.extend({});

App.ApplicationAdapter = DS.JSONAPIAdapter.extend({
  namespace: '/j89pws9vn291/pa3'
})

App.Router.map(function() {
  this.route('pic', { path: '/pic/:pic_id' });
  this.route('favorite', { path: '/favorite/:favorite_id' });
  this.route('comment', { path: '/favorite/:comment_id' }); 
  this.route('user', { path: '/user/:username'}) ;
});

App.Pic = DS.Model.extend({
  picurl: DS.attr('string'),
  prevpicid: DS.attr('string'),
  nextpicid: DS.attr('string'),
  caption: DS.attr('string'),
  favorites: DS.hasMany('favorite'),
  comments: DS.hasMany('comment')
});

App.PicRoute = Ember.Route.extend({
  model: function(params) {
    var pic = this.store.findRecord('pic', params.pic_id);
    return pic;
  },

  actions: {
    save: function() {
      var pic = this.modelFor('pic');
      var caption = this.modelFor('pic').get('caption');
      this.set('caption', caption);
      this.modelFor('pic').save();
    }
  },

  renderTemplate: function() {
    this.render('pic');
  }
});


App.Favorite = DS.Model.extend({
  username: DS.attr('string'),
  datetime: DS.attr('date'),
  pic: DS.belongsTo('pic')
});

App.FavoriteRoute = Ember.Route.extend({
  model: function() {
    return this.store.findRecord();
  }
});

App.User = DS.Model.extend({
  username: DS.attr('string'),
  firstname: DS.attr('string'),
  lastname: DS.attr('string')
});

App.UserRoute = Ember.Route.extend({
  model: function() {
    return this.store.findRecord();
  }
});

App.UsernameInputComponent = Ember.Component.extend({

  usernameValidator: Ember.inject.service(),

  focusOut: function() {
    var username = this.get('username')
    this.get('usernameValidator').validateUsername(username)
    .then(function(username) {
      console.log('username ', username, ' exists');
      $('#usernameInputError #error').remove();
    })
    .catch(function(error) {
      $('#usernameInputError').append('<div id="error">Sorry, the username does not exist.</div>');
    });
    var parent = this.get('parentView');
    parent.set('username', username);
  }
});

App.PicController = Ember.Controller.extend({

  actions: {
    commentSubmit: function(username, message) {
      var picid = this.get('model').get('id');
      var store = this.store;
      this.get('usernameValidator').validateUsername(username)
      .then(function(username) {
        $('#usernameInputError #error').remove();
        var comment = store.createRecord('comment', {
          message: message,
          username: username.get('id'),
          date: moment().format("YYYY-MM-DDTHH:mm:ss"),
        });
        var pic = store.findRecord('pic', picid)
          .then(function (pic) {
            var picurl = pic.get('picurl');
            comment.set('pic', pic);
            comment.save();
          });
      })
      .catch(function(error) {
        console.log(error);
        $('#usernameInputError').append('<div id="error">Your comment cannot be submitted as you did not provide a valid username.</div>');
        return;
      });
    }
  }
});
App.Comment = DS.Model.extend({
  pic: DS.belongsTo('pic'),
  message: DS.attr('string'),
  username: DS.attr('string'),
  date: DS.attr()
});

App.CommentRoute = Ember.Route.extend({
  model: function() {
    return this.store.findRecord();
  }
});