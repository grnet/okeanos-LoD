import DS from 'ember-data';

var inflector = Ember.Inflector.inflector;

inflector.irregular('app-action', 'apps');

export default DS.Model.extend({
  application_id: DS.attr('string'),
  lambda_instance_id: DS.attr('string'),
  call: DS.attr('string'),
});
