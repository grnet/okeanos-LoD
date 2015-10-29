import Ember from 'ember';
import DS from 'ember-data';


var inflector = Ember.Inflector.inflector;

inflector.irregular('instance-action', 'lambda-instances');

export default DS.Model.extend({
  action: DS.attr('string'),
  lambda_instance_id: DS.attr('string'),
});
