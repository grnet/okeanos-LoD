import Ember from 'ember';
import ENV from 'frontend/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {

  beforeModel: function (transition) {
    this._super(transition);
    this.store.unloadAll('lambda-instance');
    this.store.unloadAll('app-action');
    this.controllerFor('lambda-app').set('numInstances', -1);
  },

  model: function (params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
      }.bind(this));
    }, ENV.refresh_interval);

    var hash = {
      application: this.store.findRecord('lambda-app', params.app_uuid,  { reload: true }),
      instances: this.store.peekAll('lambda-instance')
    };
    if (this.store.peekAll('app-action').get('length') === 0) {
      hash.app = this.store.createRecord('app-action', {});
    }

    if (this.controllerFor('lambda-app').get('deployWait')) {
      var numInstances = hash.instances.get('length');
      var prevNumInstances = this.controllerFor('lambda-app').get('numInstances');
      if ((prevNumInstances >= 0) && (prevNumInstances !== numInstances)) {
        this.controllerFor('lambda-app').set('deployWait', false);
      }
      this.controllerFor('lambda-app').set('numInstances', numInstances);
    }

    return Ember.RSVP.hash(hash);

  },

  setupController: function (controller, model) {
    this._super(controller, model);
    controller.set('failure', false);
    controller.set('failed_delete', false);
  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
    this.controllerFor('lambda-app').set('deployWait', false);
  },

  actions: {
    error: function(error) {
      if (error && error.errors[0].status === 404) {
        this.deactivate();
        return this.transitionTo('lambda-apps.index');
      }
      return false;
    }
  }

});
