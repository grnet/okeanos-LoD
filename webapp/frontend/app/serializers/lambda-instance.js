import serializer from 'frontend/serializers/application';

export default serializer.extend(DS.EmbeddedRecordsMixin, {
  normalizeSingleResponse: function (store, primaryModelClass, payload, id, requestType) {
    payload.data[0].id = payload.data[0].attributes.info.id;
    payload.data[0].attributes.name = payload.data[0].attributes.info.name;
    for (var k in payload.data[0].attributes.info.instance_info) {
      payload.data[0].attributes[k] = payload.data[0].attributes.info.instance_info[k];
    }
    for (var k in payload.data[0].attributes.status) {
      var key = 'status_' + k;
      console.debug(key);
      payload.data[0].attributes[key] = payload.data[0].attributes.status[k];
    }
    return this._super(store, primaryModelClass, payload, id, requestType);
  }
});
