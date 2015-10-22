import Ember from 'ember';
import LoDRoute from 'frontend/routes/application';
import ENV from 'frontend/config/environment';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default LoDRoute.extend(AuthenticatedRouteMixin, {

  model: function (params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
        this.modelFor('lambda-instance').instance.reload();
      }.bind(this));
    }, ENV.refresh_interval);

    return Ember.RSVP.hash({
      instance: this.store.findRecord('lambda-instance', params.instance_uuid),
      apps: this.store.all('lambda-app')
    });

  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  }

});
