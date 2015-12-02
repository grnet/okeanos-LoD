import DS from "ember-data";

export default DS.Model.extend({
  uploadedApplications: DS.attr('number', {defaultValue: 0}),
  runningApplications: DS.attr('number', {defaultValue: 0})
});
