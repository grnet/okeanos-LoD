import Ember from "ember";

var UploadRoute  = Ember.Route.extend({
  model() {
    return Ember.RSVP.hash({
      userOkeanosProjects: this.store.findAll('user-okeanos-project')
    });
  }
});

export default UploadRoute;
