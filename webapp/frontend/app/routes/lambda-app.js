import Ember from 'ember';
import LoDRoute from 'frontend/routes/application';
import ENV from 'frontend/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default LoDRoute.extend(AuthenticatedRouteMixin, {

  model: function (params) {

    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
        this.modelFor('lambda-app').application.reload();
      }.bind(this));
    }, ENV.refresh_interval);

    return Ember.RSVP.hash({
      application: this.store.findRecord('lambda-app', params.app_uuid),
      instances: this.store.peekAll('lambda-instance'),
      app: this.store.createRecord('app-action', {}),
    });

  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  }

});
