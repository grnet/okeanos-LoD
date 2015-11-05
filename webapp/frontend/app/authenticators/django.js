import Ember from 'ember';
import Base from 'ember-simple-auth/authenticators/base';
import ENV from 'frontend/config/environment';

export default Base.extend({
  restore: function(data) {
    return new Ember.RSVP.Promise(function(resolve, reject) {
      if (!Ember.isEmpty(data.token)) {
        resolve(data);
      } else {
        reject();
      }
    });
  },

  authenticate: function(token) {
    let host = ENV.host + ':' + ENV.port,
      namespace = 'api/authenticate',
      authUrl = [ host, namespace ].join('/');
    return new Ember.RSVP.Promise((resolve, reject) => {
      Ember.$.ajax({
        url: authUrl,
        method: 'GET',
        dataType: 'json',
        headers: {'Authorization': "Token " + token},
      }).then(function(response) {
        Ember.run(function() {
          resolve({
            token: token,
            username: response.data.name
          });
        });
      }, function(xhr) {
        Ember.run(function() {
          reject(xhr);
        });
      });
    });
  },

});
