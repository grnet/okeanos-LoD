import serializer from './application'

export default serializer.extend({

  normalizeSingleResponse: function (store, primaryModelClass, payload, id, requestType) {
    payload.data[0].id = payload.data[0].attributes.info.id;
    payload.data[0].attributes = payload.data[0].attributes.info;
    for (var k in payload.data[0].attributes.instance_info) payload.data[0].attributes[k] = payload.data[0].attributes.instance_info[k];
    return this._super(store, primaryModelClass, payload, id, requestType);
  }
  
});
