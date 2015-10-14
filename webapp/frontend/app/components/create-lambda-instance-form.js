import Ember from 'ember';

export default Ember.Component.extend({
  actions: {
    create(newLambdaInstance) {
      newLambdaInstance.set('projectName', this.get('projectName'));
      newLambdaInstance.set('instanceName', this.get('instanceName'));
      newLambdaInstance.set('masterName', this.get('masterName'));
      
      newLambdaInstance.set('slaves', this.$("input[name='slaves']")[0].value);

      newLambdaInstance.set('VCPUsMaster', this.$("select[name='vcpus_master']")[0].value);
      newLambdaInstance.set('VCPUsSlave', this.$("select[name='vcpus_slave']")[0].value);
      newLambdaInstance.set('RamMaster', this.$("select[name='ram_master']")[0].value);
      newLambdaInstance.set('RamSlave', this.$("select[name='ram_slave']")[0].value);
      newLambdaInstance.set('DiskMaster', this.$("select[name='disk_master']")[0].value);
      newLambdaInstance.set('DiskSlave', this.$("select[name='disk_slave']")[0].value);
      
      newLambdaInstance.set('ipAllocation', this.$("select[name='ip_allocation']")[0].value);
      //newLambdaInstance.set('publicKeyName', this.$("select[name='public_key_name']")[0].value);

      newLambdaInstance.save();
    }
  }
});