import LoDSerializer from 'frontend/serializers/application';
import Ember from "ember";
import DS from 'ember-data';

export default LoDSerializer.extend(DS.EmbeddedRecordsMixin, {
  normalizeSingleResponse: function (store, primaryModelClass, payload, id, requestType) {
    payload.data[0].id = payload.data[0].attributes.info.id;
    payload.data[0].attributes.name = payload.data[0].attributes.info.name;
    var k;
    for (k in payload.data[0].attributes.info.instance_info) {
      payload.data[0].attributes[k] = payload.data[0].attributes.info.instance_info[k];
    }
    for (k in payload.data[0].attributes.status) {
      var key = 'status_' + k;
      payload.data[0].attributes[key] = payload.data[0].attributes.status[k];
    }
    for (k in payload.data[0].applications) {
      payload.data[0].applications[k].app_type = payload.data[0].applications[k].type;
      payload.data[0].applications[k].type = 'lambda-app';
    }
    for (k in payload.data[0].applications) {
      payload.data[0].applications[k].attributes = Ember.$.extend(true, {}, payload.data[0].applications[k]);
    }
    payload.included = payload.data[0].applications;
    delete payload.data[0].attributes.applications;
    delete payload.data[0].attributes.info;
    delete payload.data[0].attributes.status;
    return this._super(store, primaryModelClass, payload, id, requestType);
  }
});
