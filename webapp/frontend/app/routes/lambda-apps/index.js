import Ember from 'ember';
import ENV from 'frontend/config/environment';
import LoDRoute from 'frontend/routes/application';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default LoDRoute.extend(AuthenticatedRouteMixin, {
  model: function(params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
      }.bind(this));
    }, ENV.refresh_interval);

    return this.store.findAll('lambda-app', params);
  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  }

});
