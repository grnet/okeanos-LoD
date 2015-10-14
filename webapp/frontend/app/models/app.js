import DS from 'ember-data';

var inflector = Ember.Inflector.inflector;

inflector.irregular('app', 'apps/');

export default DS.Model.extend({
  description: DS.attr('string'),
  file: DS.attr(),
  type: DS.attr('string'),
  project_name: DS.attr('string'),
});
