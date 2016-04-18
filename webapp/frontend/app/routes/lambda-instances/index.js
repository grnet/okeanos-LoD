import Ember from 'ember';
import ENV from 'frontend/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {

  beforeModel: function (transition) {
    this._super(transition);
    this.store.unloadAll('instance-action');
    this.store.unloadAll('lambda-instance');
    this.store.unloadAll('lambda-app');
  },

  model: function(params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
      }.bind(this));
    }, ENV.refresh_interval);

    var hash = {
      instances: this.store.findAll('lambda-instance', params, { reload: true }),
    };
    if (this.store.peekAll('instance-action').get('length') === 0) {
      hash.instance_action = this.store.createRecord('instance-action', {});
    }

    var _this = this;
    return Ember.RSVP.hash(hash).then(function (hash) {
      if (!_this.controllerFor('lambda-instances.index').get('showFailed')) {
        hash.instances.forEach(function (instance) {
          let status_code = instance.get('status_code');
          if (status_code >= 9 && status_code <=23 && (status_code % 2) === 1) {
            instance.unloadRecord();
          }
        });
      }
      _this.controllerFor('lambda-instances.index').send('checkPage');
      return hash;
    });

  },

  setupController: function (controller, model) {
    controller.set('content', model.instances);
    controller.set('instance_action', model.instance_action);
    controller.set('failure', false);
    controller.set('failed_delete', false);
    controller.send('checkPage');
  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  }

});
