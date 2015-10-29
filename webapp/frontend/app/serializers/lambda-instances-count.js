import GenericSerializer from "frontend/serializers/application";

export default GenericSerializer.extend({
  normalizeResponse: function(store, primaryModelClass, payload, id, requestType){
    // The API call doen't include an id-like attribute in the response. Add an auto-increment
    // id to be able to use the default serializer.
    for(var i = 0;i < payload.data.length;i++){
      payload.data[i]['id'] = i;
    }

    return this._super(store, primaryModelClass, payload, id, requestType);
  }
});
