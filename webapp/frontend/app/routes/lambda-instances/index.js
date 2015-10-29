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

    var hash = {
      instances: this.store.findAll('lambda-instance', params),
      apps: this.store.peekAll('lambda-app'),
    };
    if (this.store.peekAll('instance-action').get('length') === 0) {
      hash.instance_action = this.store.createRecord('instance-action', {});
    }
    return Ember.RSVP.hash(hash);

  },

  setupController: function(controller, model) {
      controller.set('content', model.instances);
      controller.set('instance_action', model.instance_action);
      controller.set('apps', model.apps);
  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  }

});
