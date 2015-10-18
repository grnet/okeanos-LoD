import DS from "ember-data";

export default DS.Model.extend({
  vcpus: DS.attr({defaultValue: []}),
  ram: DS.attr({defaultValue: []}),
  disk: DS.attr({defaultValue: []})
});
