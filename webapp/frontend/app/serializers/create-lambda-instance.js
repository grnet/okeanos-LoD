import Ember from "ember";
import DS from 'ember-data';

export default DS.JSONSerializer.extend({
  keyForAttribute: function (attr) {
    return Ember.String.underscore(attr);
  },
  extractErrors: function(store, typeClass, payload) {
    var transformedErrors = {};
    for(var i = 0;i < payload.errors.length;i++){
      var detail = payload.errors[i].detail[0].split(": ");
      var parameter = detail[0];
      var message = detail[1];
      transformedErrors[Ember.String.camelize(parameter)] = [message];
    }
    payload.errors = transformedErrors;

    return payload.errors;
  }
});
