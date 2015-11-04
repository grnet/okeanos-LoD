import Ember from "ember";
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

var UploadRoute  = Ember.Route.extend(AuthenticatedRouteMixin, {

  model() {
    return Ember.RSVP.hash({
      userOkeanosProjects: this.store.findAll('user-okeanos-project')
    });
  },
  
  actions:{
      willTransition(transition) {
        if (this.controller.get('userHasEnteredData') &&
            !confirm("Upload in progress.Are you sure you want to leave the page?")) {
          transition.abort();
        }
      },
  },
});

export default UploadRoute;
