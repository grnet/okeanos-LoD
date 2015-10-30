import Ember from "ember";
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model() {
    return Ember.RSVP.hash({
      lambdaInstancesCount: this.store.findRecord('lambda-instances-count'),
      applicationsCount: this.store.findRecord('applications-count')
    });
  }
});
