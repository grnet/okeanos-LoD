import Ember from 'ember';
import DS from 'ember-data';

export default DS.JSONAPISerializer.extend({
  normalizeArrayResponse: function(store, primaryModelClass, payload, id, requestType) {
    var pluralTypeKey = Ember.Inflector.inflector.pluralize(primaryModelClass.modelName);
    for (var i=0;i<payload.data.length;++i) {
      var status = Ember.$.extend(true, {}, payload.data[i].status);
      console.debug('status');
      console.debug(status);
      delete payload.data[i].status;
      payload.data[i].attributes = Ember.$.extend(true, {}, payload.data[i]);
      payload.data[i].attributes.uuid = payload.data[i].id;
      payload.data[i].attributes.status = status.detail;
      payload.data[i].attributes.failure_message = status.failure_message;
      payload.data[i].type = pluralTypeKey;
    }
    delete payload.status;
    return payload;
  }

});
