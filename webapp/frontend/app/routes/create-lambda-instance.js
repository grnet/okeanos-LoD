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
  afterModel: function(model) {
    // After the models are loaded, check each project's quotas. If a least one project
    // has enough quotas to create a Lambda Instance, set enoughQuotas to true.
    // Delete every project that doesn't have the quotas to create the smallest Lambda
    // Instance.
    var controller = this.controllerFor('create-lambda-instance');
    var minQuotasPerProject = controller.get('minQuotasPerProject');
    for (var i = 0;i < model.userOkeanosProjects.get('length');i++){
    	if (model.userOkeanosProjects.objectAt(i).get('vm') >= minQuotasPerProject['vms'] &&
    	    model.userOkeanosProjects.objectAt(i).get('cpu') >= minQuotasPerProject['cpus'] &&
    	    model.userOkeanosProjects.objectAt(i).get('ram') >= minQuotasPerProject['ram']['bytes'] &&
    	    model.userOkeanosProjects.objectAt(i).get('disk') >= minQuotasPerProject['disk']['bytes'] &&
    	    model.userOkeanosProjects.objectAt(i).get('floating_ip') >= minQuotasPerProject['floatingIPs'] &&
    	    model.userOkeanosProjects.objectAt(i).get('private_network') >= minQuotasPerProject['privateNetworks']) {

        if(!controller.get('enoughQuotas')){
    		  controller.set('enoughQuotas', true);
        }
    	}
      else{
        model.userOkeanosProjects.objectAt(i).deleteRecord();
      }
    }

    // If at least one project has enough quotas, set the default values for the drop down lists.
    if(model.userOkeanosProjects.get('length') > 0){
      controller.set('selectedProject', model.userOkeanosProjects.objectAt(0).get('name'));
      controller.set('selectedNumberOfSlaves', minQuotasPerProject['vms'] - 1);

      var minQuotasPerVM = controller.get('minQuotasPerVM');
      controller.set('selectedMasterNodeCPUs', minQuotasPerVM['cpus']);
      controller.set('selectedSlaveNodeCPUs', minQuotasPerVM['cpus']);
      controller.set('selectedMasterNodeRAM', minQuotasPerVM['ram']);
      controller.set('selectedSlaveNodeRAM', minQuotasPerVM['ram']);
      controller.set('selectedMasterNodeDisk', minQuotasPerVM['disk']);
      controller.set('selectedSlaveNodeDisk', minQuotasPerVM['disk']);

      controller.set('masterNodeCPUValues', model.VMParameterValues.objectAt(0).get('vcpus'));
      controller.set('slaveNodeCPUValues', model.VMParameterValues.objectAt(0).get('vcpus'));
      controller.set('masterNodeRAMValues', model.VMParameterValues.objectAt(0).get('ram'));
      controller.set('slaveNodeRAMValues', model.VMParameterValues.objectAt(0).get('ram'));
      controller.set('masterNodeDiskValues', model.VMParameterValues.objectAt(0).get('disk'));
      controller.set('slaveNodeDiskValues', model.VMParameterValues.objectAt(0).get('disk'));
    }
  }
});
