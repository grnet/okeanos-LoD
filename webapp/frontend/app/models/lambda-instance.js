import DS from "ember-data";

// Information about user
var LambdaInstance = DS.Model.extend({
  name: DS.attr(),
  project_name : DS.attr('string'),  // project of the lambda instance
  instance_name : DS.attr('string'),    // name of the lambda instance
  slaves : DS.attr('number'),     // size of cluster
  vcpus_master : DS.attr('number'),     // cpus of master
  vcpus_slave : DS.attr('number'),		  // cpus of each slave00
  ram_master : DS.attr('number'),		    // disk for master
  ram_slave : DS.attr('number'),		    // ram of each slave
  disk_master : DS.attr('number'),		  // disk of master
  disk_slave : DS.attr('number'),		    // disk of each slave
});

export default LambdaInstance;
