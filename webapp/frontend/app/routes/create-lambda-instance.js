import Ember from "ember";
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

export default Ember.Route.extend(AuthenticatedRouteMixin, {
  model: function() {
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

    controller.set('enoughQuotas', false);

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
  },
  setupController: function(controller, model){
    this._super(controller, model);

    if(model.userOkeanosProjects.get('length') > 0){
      var minQuotasPerProject = controller.get('minQuotasPerProject');

      var selectedProject = model.userOkeanosProjects.objectAt(0);
      controller.set('selectedProjectName', selectedProject.get('name'));
      controller.set('selectedProjectVMs', selectedProject.get('vm'));
      controller.set('selectedProjectCPUs', selectedProject.get('cpu'));
      controller.set('selectedProjectRAM', {'megaBytes': selectedProject.get('ram') / 1048576});
      controller.set('selectedProjectDisk', {'gigaBytes': selectedProject.get('disk') / 1073741824});
      controller.set('selectedNumberOfSlaves', minQuotasPerProject['vms'] - 1);

      var minQuotasPerVM = controller.get('minQuotasPerVM');

      var masterNodeCPUValues = controller.get('masterNodeCPUValues');
      var slaveNodeCPUValues = controller.get('slaveNodeCPUValues');

      var masterNodeRAMValues = controller.get('masterNodeRAMValues');
      var slaveNodeRAMValues = controller.get('slaveNodeRAMValues');

      var masterNodeDiskValues = controller.get('masterNodeDiskValues');
      var slaveNodeDiskValues = controller.get('slaveNodeDiskValues');

      var n = model.VMParameterValues.get('length');
      for(var i = 0;i < n;i++){

        var cpus = model.VMParameterValues.objectAt(i).get('vcpus');
        for(var j = 0, m = cpus.get('length');j < m;j++){
          if(cpus[j] >= minQuotasPerVM['cpus']){
            masterNodeCPUValues.pushObject(Ember.Object.create({'value': parseInt(cpus[j]), 'enabled': true}));
            slaveNodeCPUValues.pushObject(Ember.Object.create({'value': parseInt(cpus[j]), 'enabled': true}));
          }
        }

        var ram = model.VMParameterValues.objectAt(i).get('ram');
        for(j = 0, m = ram.get('length');j < m;j++){
          if(ram[j] >= minQuotasPerVM['ram']){
            masterNodeRAMValues.pushObject(Ember.Object.create({'value': parseInt(ram[j]), 'enabled': true}));
            slaveNodeRAMValues.pushObject(Ember.Object.create({'value': parseInt(ram[j]), 'enabled': true}));
          }
        }

        var disk = model.VMParameterValues.objectAt(i).get('disk');
        for(j = 0, m = disk.get('length');j < m;j++){
          if(disk[j] >= minQuotasPerVM['disk']){
            masterNodeDiskValues.pushObject(Ember.Object.create({'value': parseInt(disk[j]), 'enabled': true}));
            slaveNodeDiskValues.pushObject(Ember.Object.create({'value': parseInt(disk[j]), 'enabled': true}));
          }
        }
      }

      var compareFunction = function(a, b){
        return a['value'] > b['value'];
      };

      masterNodeCPUValues.sort(compareFunction);
      slaveNodeCPUValues.sort(compareFunction);

      masterNodeRAMValues.sort(compareFunction);
      slaveNodeRAMValues.sort(compareFunction);

      masterNodeDiskValues.sort(compareFunction);
      slaveNodeDiskValues.sort(compareFunction);

      controller.set('selectedMasterNodeCPUs', masterNodeCPUValues[0]['value']);
      controller.set('selectedSlaveNodeCPUs', slaveNodeCPUValues[0]['value']);

      controller.set('selectedMasterNodeRAM', masterNodeRAMValues[0]['value']);
      controller.set('selectedSlaveNodeRAM', slaveNodeRAMValues[0]['value']);

      controller.set('selectedMasterNodeDisk', masterNodeDiskValues[0]['value']);
      controller.set('selectedSlaveNodeDisk', slaveNodeDiskValues[0]['value']);

      controller.set('kafkaInputTopics', ["input"]);
      controller.set('kafkaOutputTopics', ["batch-output", "stream-output"]);
    }
  }
});
