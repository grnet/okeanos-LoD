import Ember from "ember";
import DS from 'ember-data';

export default DS.JSONAPISerializer.extend({

  keyForAttribute: function (attr) {
    return Ember.String.underscore(attr);
  },

  normalizeResponse: function (store, primaryModelClass, payload, id, requestType) {
    for (var i = 0; i < payload.data.length; i++) {
      payload.data[i].attributes = Ember.$.extend(true, {}, payload.data[i]);
      payload.data[i].type = primaryModelClass.modelName;
    }
    delete payload.status;
    return this._super(store, primaryModelClass, payload, id, requestType);
  },

  normalizeSingleResponse: function (store, primaryModelClass, payload, id, requestType) {
    payload.data = payload.data[0];
    return this._super(store, primaryModelClass, payload, id, requestType);
  },

  removeDeleted: function (store, modelName, payload) {
    var oldRecords = this.store.peekAll(modelName);
    var record;
    oldRecords.forEach (function (oldRecord) {
      if (!payload.data.isAny('id', oldRecord.id)) {
        record = store.peekRecord(modelName, oldRecord.id);
        store.unloadRecord(record);
      }
    });
  },

});
