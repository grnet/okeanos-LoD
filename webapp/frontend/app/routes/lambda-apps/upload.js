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
            !confirm("Upload is in progress. Are you sure you want to leave the page?")) {
          transition.abort();
        }
      },
  },

  afterModel: function(model) {
    // After the models are loaded, check each project's quotas. If a least one project
    // has enough quotas to upload a Lambda Application, set enoughQuotas to true.
    // Delete every project that has no quotas on Pithos+.

    var controller = this.controllerFor('lambda-apps.upload');
    controller.set('enoughQuotas', false);

    for (var i = 0;i < model.userOkeanosProjects.get('length');i++){
      if (model.userOkeanosProjects.objectAt(i).get('pithos_space') > 0) {
        if(!controller.get('enoughQuotas')){
          controller.set('enoughQuotas', true);
        }
      }
      else{
        model.userOkeanosProjects.objectAt(i).deleteRecord();
      }
    }
  }
});

export default UploadRoute;
