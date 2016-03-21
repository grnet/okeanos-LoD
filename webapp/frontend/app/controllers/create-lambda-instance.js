import Ember from "ember";

export default Ember.Controller.extend({
  selectedProject: null,
  selectedNumberOfSlaves: null,
  selectedMasterNodeCPUs: null,
  selectedSlaveNodeCPUs: null,
  selectedMasterNodeRAM: null,
  selectedSlaveNodeRAM: null,
  selectedMasterNodeDisk: null,
  selectedSlaveNodeDisk: null,

  masterNodeCPUValues: [],
  slaveNodeCPUValues: [],
  masterNodeRAMValues: [],
  slaveNodeRAMValues: [],
  masterNodeDiskValues: [],
  slaveNodeDiskValues: [],

  minQuotasPerVM: {'cpus': 2, 'ram': 2048, 'disk': 10},
  minQuotasPerProject: {
    'vms': 2,
    'cpus': 4,
    'ram': {"bytes": 4294967296, "megaBytes": 4096},
    'disk': {"bytes": 21474836480, "gigaBytes": 20},
    'floatingIPs': 1,
    'privateNetworks': 1
  },

  enoughQuotas: false,

  actions: {
    saveLambdaInstance: function(newLambdaInstance){
      newLambdaInstance.set('instanceName', this.get('instanceName'));
      newLambdaInstance.set('masterName', this.get('masterName'));

      newLambdaInstance.set('slaves', this.$("input[name='slaves']")[0].value);

      newLambdaInstance.set('projectName', this.$("select[name='okeanos_project']")[0].value);
      newLambdaInstance.set('VCPUsMaster', this.$("select[name='vcpus_master']")[0].value);
      newLambdaInstance.set('VCPUsSlave', this.$("select[name='vcpus_slave']")[0].value);
      newLambdaInstance.set('RamMaster', this.$("select[name='ram_master']")[0].value);
      newLambdaInstance.set('RamSlave', this.$("select[name='ram_slave']")[0].value);
      newLambdaInstance.set('DiskMaster', this.$("select[name='disk_master']")[0].value);
      newLambdaInstance.set('DiskSlave', this.$("select[name='disk_slave']")[0].value);

      var requestedPublicKeys = [];
      var options = this.$("select[name='public_key_name']")[0].options;
      for(var i = 0;i < options.length;i++){
        if(options[i].selected){
          requestedPublicKeys.push(options[i].value);
        }
      }
      newLambdaInstance.set('publicKeyName', requestedPublicKeys);

      var kafkaOutputTopics, kafkaInputTopics;

      var kafkaInputTopicsString = this.get('kafkaInputTopics');
      if (kafkaInputTopicsString) {
        kafkaInputTopics = kafkaInputTopicsString.replace(/\s+/g, '').split(',');
      }

      var kafkaOutputTopicsString = this.get('kafkaOutputTopics');
      if (kafkaOutputTopicsString) {
        kafkaOutputTopics = kafkaOutputTopicsString.replace(/\s+/g, '').split(',');
      }

      var duplicateTopic = false;
      if (kafkaInputTopics && kafkaOutputTopics) {
        kafkaInputTopics.forEach(function (inputTopic) {
          if (kafkaOutputTopics.indexOf(inputTopic) !== -1) {
            duplicateTopic = true;
          }
        });
      }

      if (duplicateTopic) {
        this.set('duplicate_message', 'Apache Kafka input and output topics must be different!');
        this.set('duplicate', true);
        document.getElementById('inputTopics').focus();
      }
      else {
        newLambdaInstance.set('kafkaInputTopics', kafkaInputTopics);
        newLambdaInstance.set('kafkaOutputTopics', kafkaOutputTopics);

        var self = this;
        newLambdaInstance.save().then(function(){
          self.transitionToRoute('lambda-instance', newLambdaInstance.get('id')).catch(function() {
            self.transitionToRoute('lambda-instances.index').then(function(newRoute) {
              newRoute.controller.set('message', 'Your lambda instance creation will begin shortly.');
              newRoute.controller.set('request', true);
              newRoute.controller.send('start_stop');
            });
          });
        });
      }
    },

    close_alert: function()
    {
      this.set('duplicate', false);
    },

    selectFromDropDownList: function(variable, event){
      var value = event.target.value;
      this.set(variable, value);

      this.calculateDropDownListValues();
    }
  },

  calculateDropDownListValues: function(){

  }
});
