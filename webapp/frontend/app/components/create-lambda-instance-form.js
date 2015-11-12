import Ember from 'ember';

export default Ember.Component.extend({
  actions: {
    create(newLambdaInstance) {
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

      var kafkaInputTopicsString = this.get("kafkaInputTopics");
      if (kafkaInputTopicsString) {
        newLambdaInstance.set('kafkaInputTopics', kafkaInputTopicsString.split(','));
      }

      var kafkaOutputTopicsString = this.get("kafkaOutputTopics");
      if (kafkaOutputTopicsString) {
        newLambdaInstance.set('kafkaOutputTopics', kafkaOutputTopicsString.split(','));
      }

      this.sendAction('saveAction', newLambdaInstance);
    }
  }
});
