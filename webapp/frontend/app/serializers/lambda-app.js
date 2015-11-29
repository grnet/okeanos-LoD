import LoDSerializer from 'frontend/serializers/application';
import Ember from "ember";
import DS from 'ember-data';

export default LoDSerializer.extend(DS.EmbeddedRecordsMixin, {
  normalizeSingleResponse: function (store, primaryModelClass, payload, id, requestType) {
    let k;
    payload.data[0].attributes.app_type = payload.data[0].attributes.type;
    for (k in payload.data[0].attributes.status) {
      let key = 'status_' + k;
      payload.data[0].attributes[key] = payload.data[0].attributes.status[k];
    }
    let li;
    let s, key;
    for (k in payload.data[0].attributes.lambda_instances) {
      li = payload.data[0].attributes.lambda_instances[k];
      li.type = 'lambda-instance';
      li.attributes = Ember.$.extend(true, {}, li);
      li.attributes.started_app = li.attributes.started;
      for (s in li.attributes.status) {
        key = 'status_' + s;
        li.attributes[key] = li.attributes.status[s];
       }
    }
    payload.included = payload.data[0].attributes.lambda_instances;
    this.removeDeleted(store, 'lambda-instance', payload.included);
    delete payload.data[0].attributes.lambda_instances;
    delete payload.data[0].attributes.status;
    return this._super(store, primaryModelClass, payload, id, requestType);
  },

  normalizeArrayResponse: function(store, primaryModelClass, payload, id, requestType) {
    for (var i=0;i<payload.data.length;++i) {
      payload.data[i].attributes.app_type = payload.data[i].attributes.type;
      for (var k in payload.data[i].attributes.status) {
        var key = 'status_' + k;
        payload.data[i].attributes[key] = payload.data[i].attributes.status[k];
      }
    }
    this.removeDeleted(store, primaryModelClass.modelName, payload.data);
    return this._super(store, primaryModelClass, payload, id, requestType);
  }
});
