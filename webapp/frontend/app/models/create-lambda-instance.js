import DS from "ember-data";

export default DS.Model.extend({
  projectName: DS.attr('string', {defaultValue: "lambda.grnet.gr"}),
  instanceName: DS.attr('string', {defaultValue: "My Lambda Instance"}),
  masterName: DS.attr('string', {defaultValue: "Lambda Instance Master Node"}),
  slaves: DS.attr('number', {defaultValue: 2}),
  VCPUsMaster: DS.attr('number', {defaultValue: 4}),
  VCPUsSlave: DS.attr('number', {defaultValue: 4}),
  RamMaster: DS.attr('number', {defaultValue: 4096}),
  RamSlave: DS.attr('number', {defaultValue: 4096}),
  DiskMaster: DS.attr('number',  {defaultValue: 20}),
  DiskSlave: DS.attr('number',  {defaultValue: 20}),
  ipAllocation: DS.attr('string',  {defaultValue: "master"}),
  publicKeyName: DS.attr({defaultValue: []}),
  kafkaInputTopics: DS.attr(),
  kafkaOutputTopics: DS.attr()
});
