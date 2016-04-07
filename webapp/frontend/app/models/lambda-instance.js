import DS from "ember-data";

// Information about lambda instance
var LambdaInstance = DS.Model.extend({
  name: DS.attr(),                          // name of lambda instance
  project_name: DS.attr(),                  // project of lambda instance
  slaves: DS.attr('number'),                // number of slaves
  master_name: DS.attr(),                   // name of master
  master_node_id: DS.attr('number'),        // id of master
  vcpus_master: DS.attr('number'),          // cpus of master
  vcpus_slave: DS.attr('number'),           // cpus of each slave
  ram_master: DS.attr('number'),            // disk for master
  ram_slave: DS.attr('number'),             // ram of each slave
  disk_master: DS.attr('number'),           // disk of master
  disk_slave: DS.attr('number'),            // disk of each slave
  public_key_name: DS.attr(),               // ~okeanos public keys
  status_message: DS.attr(),                // status of lambda instance
  status_code: DS.attr('number'),           // status code of lambda instance
  status_detail: DS.attr(),                 // status detail of lambda instance
  status_failure_message: DS.attr(),        // failure message
  applications: DS.hasMany('lambda-app'),   // deployed applications
  started_app: DS.attr('boolean'),          // is specific app started?
  running_app: DS.attr('boolean'),          // is any app running on the lambda instance?
  kafka_input_topics: DS.attr(),            // kafka input topics of lambda instance
  kafka_output_topics: DS.attr(),           // kafka output topics of lambda instance
  deleting: DS.attr('boolean')              // has a delete request been sent?
});

export default LambdaInstance;
