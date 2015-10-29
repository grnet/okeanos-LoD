import Ember from "ember";
import DS from 'ember-data';

export default DS.JSONSerializer.extend({
  attrs: {
    lambda_instance_id: {serialize: false}
  },
  extractErrors: function(store, typeClass, payload) {
    var transformedErrors = {};
    for(var i = 0;i < payload.errors.length;i++){
      var message = payload.errors[i].detail;
      var parameter = "detail";
      transformedErrors[Ember.String.camelize(parameter)] = [message];
    }
    payload.errors = transformedErrors;
    return payload.errors;
  },
});
