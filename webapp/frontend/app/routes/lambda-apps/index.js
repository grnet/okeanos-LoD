import Ember from 'ember';
import ENV from 'frontend/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {

  beforeModel: function (transition) {
    this._super(transition);
    this.store.unloadAll('lambda-app');
  },

  model: function(params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
      }.bind(this));
    }, ENV.refresh_interval);

    return this.store.findAll('lambda-app', params, { reload: true });
  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  },

  setupController: function (controller, model ) {
    this._super(controller, model);
    controller.send('checkPage');
  },

});
