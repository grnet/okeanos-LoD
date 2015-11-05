import Ember from "ember";
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model() {
    return Ember.RSVP.hash({
      newLambdaInstance: this.store.createRecord('create-lambda-instance', {}),
      userPublicKeys: this.store.findAll('user-public-key'),
      userOkeanosProjects: this.store.findAll('user-okeanos-project'),
      VMParameterValues: this.store.findAll('vm-parameter-value')
    });
  },
  afterModel: function(model, transition) {
    for (var i = 0;i < model.userOkeanosProjects.get('length');i++){
    	if (model.userOkeanosProjects.objectAt(i).get('vm') >= 2 &&
    	    model.userOkeanosProjects.objectAt(i).get('cpu') >= 4 &&
    	    model.userOkeanosProjects.objectAt(i).get('ram') >= 4294967296 &&
    	    model.userOkeanosProjects.objectAt(i).get('disk') >= 21474836480 &&
    	    model.userOkeanosProjects.objectAt(i).get('floating_ip') >= 1 &&
    	    model.userOkeanosProjects.objectAt(i).get('private_network') >= 1) {
    		this.controllerFor('create-lambda-instance').set('enoughQuotas', true);
    	}
    }
  }
});
