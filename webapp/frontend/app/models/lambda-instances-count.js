import DS from "ember-data";

export default DS.Model.extend({
  count: DS.attr('number', {defaultValue: 0})
});
