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
    for (k in payload.data[0].attributes.lambda_instances) {
      li = payload.data[0].attributes.lambda_instances[k];
      li.type = 'lambda-instance';
      li.attributes = Ember.$.extend(true, {}, li);
      li.attributes.started_app = li.attributes.started;
    }
    payload.included = payload.data[0].attributes.lambda_instances;
    delete payload.data[0].attributes.lambda_instances;
    delete payload.data[0].attributes.status;
    return this._super(store, primaryModelClass, payload, id, requestType);
  }
});
