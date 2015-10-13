import Ember from 'ember';
import DS from 'ember-data';

export default DS.JSONAPISerializer.extend({
  normalizeArrayResponse: function(store, primaryModelClass, payload, id, requestType) {
    var pluralTypeKey = Ember.Inflector.inflector.pluralize(primaryModelClass.modelName);
    for (var i=0;i<payload.data.length;++i) {
      payload.data[i].attributes = payload.data[i];
      payload.data[i].attributes.uuid = payload.data[i].id;
      payload.data[i].type = pluralTypeKey;
    }
    delete payload.status;
    return payload;
  }

});
