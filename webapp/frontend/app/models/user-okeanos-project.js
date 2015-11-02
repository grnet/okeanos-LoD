import DS from "ember-data";

export default DS.Model.extend({
  name: DS.attr('string'),
  vm: DS.attr('number'),
  cpu: DS.attr('number'),
  ram: DS.attr('number'),
  disk: DS.attr('number'),
  floating_ip: DS.attr('number'),
  private_network: DS.attr('number'),
  pithos_space: DS.attr('number')
});
