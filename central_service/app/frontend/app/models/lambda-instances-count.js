import DS from "ember-data";

export default DS.Model.extend({
  runningLambdaInstances: DS.attr('number', {defaultValue: 0}),
  createdLambdaInstances: DS.attr('number', {defaultValue: 0})
});
