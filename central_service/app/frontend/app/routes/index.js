import Ember from "ember";

export default Ember.Route.extend({
  model() {
    return Ember.RSVP.hash({
      lambdaInstancesCount: this.store.findRecord('lambda-instances-count'),
      applicationsCount: this.store.findRecord('applications-count'),
      usersCount: this.store.findRecord('users-count')
    });
  }
});
