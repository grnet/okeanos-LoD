import Ember from "ember";
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

var UploadRoute  = Ember.Route.extend(AuthenticatedRouteMixin, {
  model() {
    return Ember.RSVP.hash({
      userOkeanosProjects: this.store.findAll('user-okeanos-project')
    });
  }
});

export default UploadRoute;
