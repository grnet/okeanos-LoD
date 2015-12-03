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
        this.sendAction('saveAction', newLambdaInstance);
      }
    },

    close_alert: function()
    {
      this.set('duplicate', false);
    },
  }
});
