import Ember from "ember";
import LoDRoute from 'frontend/routes/application';

export default LoDRoute.extend({
  model() {
    return Ember.RSVP.hash({
      newLambdaInstance: this.store.createRecord('create-lambda-instance', {}),
      userPublicKeys: this.store.findAll('user-public-key'),
      userOkeanosProjects: this.store.findAll('user-okeanos-project'),
      VMParameterValues: this.store.findAll('vm-parameter-value')
    });
  }
});
