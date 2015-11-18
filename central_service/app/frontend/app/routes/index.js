import Ember from "ember";

export default Ember.Route.extend({
  model: function() {
  	this.poll = Ember.run.later(this, function () {
	    this.model();
	}, 30000);

    return Ember.RSVP.hash({
      lambdaInstancesCount: this.store.findAll('lambda-instances-count'),
      applicationsCount: this.store.findAll('applications-count'),
      usersCount: this.store.findAll('users-count')
    });
  },
  deactivate: function () {
    Ember.run.cancel(this.poll);
  }
});
