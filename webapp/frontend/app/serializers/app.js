import Ember from "ember";
import DS from 'ember-data';

export default DS.JSONSerializer.extend({
  attrs: {
    call: {serialize: false}
  },
  keyForAttribute: function (attr) {
    return Ember.String.dasherize(attr);
  },
});
