import Ember from 'ember';
import ENV from 'frontend/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {

  beforeModel: function (transition) {
    this._super(transition);
    this.store.unloadAll('lambda-app');
    this.store.unloadAll('app-action');
  },

  model: function (params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
        this.modelFor('lambda-instance').instance.reload();
      }.bind(this));
    }, ENV.refresh_interval);

    var hash = {
      instance: this.store.findRecord('lambda-instance', params.instance_uuid),
      apps: this.store.peekAll('lambda-app'),
    };
    if (this.store.peekAll('app-action').get('length') === 0) {
      hash.app = this.store.createRecord('app-action', {});
    }
    if (this.store.peekAll('instance-action').get('length') === 0) {
      hash.instance_action = this.store.createRecord('instance-action', {});
    }
    return Ember.RSVP.hash(hash);

  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  }

});
