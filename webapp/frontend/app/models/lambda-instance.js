import DS from "ember-data";

// Information about lambda instance
var LambdaInstance = DS.Model.extend({
  name: DS.attr(),                  // name of the lambda instance
  project_name: DS.attr(),          // project of the lambda instance
  slaves: DS.attr('number'),        // number of slaves
  master_name: DS.attr(),           // name of master
  vcpus_master: DS.attr('number'),  // cpus of master
  vcpus_slave: DS.attr('number'),		// cpus of each slave
  ram_master: DS.attr('number'),		// disk for master
  ram_slave: DS.attr('number'),		  // ram of each slave
  disk_master: DS.attr('number'),		// disk of master
  disk_slave: DS.attr('number'),		// disk of each slave
  public_key_name: DS.attr()        // ~okeanos public keys
});

export default LambdaInstance;
