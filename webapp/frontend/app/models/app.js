import DS from 'ember-data';

export default DS.Model.extend({
  application_id: DS.attr('string'),
  lambda_instance_id: DS.attr('string'),
});
