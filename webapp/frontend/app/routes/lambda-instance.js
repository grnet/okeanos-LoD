import Ember from 'ember';
import ENV from 'frontend/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {

  beforeModel: function (transition) {
    this._super(transition);
    this.store.unloadAll('lambda-app');
    this.store.unloadAll('app-action');
    this.store.unloadAll('instance-action');
  },

  model: function (params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
      }.bind(this));
    }, ENV.refresh_interval);

    var hash = {
      instance: this.store.findRecord('lambda-instance', params.instance_uuid,  { reload: true }),
      apps: this.store.peekAll('lambda-app')
    };
    if (this.store.peekAll('app-action').get('length') === 0) {
      hash.app = this.store.createRecord('app-action', {});
    }
    if (this.store.peekAll('instance-action').get('length') === 0) {
      hash.instance_action = this.store.createRecord('instance-action', {});
    }

    var _this = this;
    return Ember.RSVP.hash(hash).then(function (hash) {
      if (_this.controllerFor('lambda-instance').get('deployWait')) {
        var deployID = _this.controllerFor('lambda-instance').get('deployID');
        hash.apps.forEach(function (app) {
          if (app.id === deployID) {
            _this.controllerFor('lambda-instance').set('deployWait', false);
          }
        });
      }
      return hash;
    });

  },

  setupController: function (controller, model) {
    this._super(controller, model);
    controller.set('failure', false);
    controller.set('failed_delete', false);
  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
    this.controllerFor('lambda-instance').set('deployWait', false);
    this.controllerFor('lambda-instance').set('deployID', -1);
  },

  actions: {
    error: function(error) {
      if (error && error.errors[0].status === 404) {
        this.deactivate();
        return this.transitionTo('lambda-instances.index');
      }
      return false;
    }
  }

});
