import Ember from 'ember';
import ENV from 'frontend/config/environment';
import LoDRoute from 'frontend/routes/application';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default LoDRoute.extend(AuthenticatedRouteMixin, {
  model: function(params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
        this.store.findAll('lambda-instance', params);
      }.bind(this));
    }, ENV.refresh_interval+1000);

    return this.store.findAll('lambda-instance', params);
  }
});
