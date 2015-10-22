import LoDRoute from 'frontend/routes/application';
import UnauthenticatedRouteMixin from 'ember-simple-auth/mixins/unauthenticated-route-mixin';

export default LoDRoute.extend(UnauthenticatedRouteMixin, {
  setupController: function() {
  }
});
