import LoDAdapter from 'frontend/adapters/application';
import DS from 'ember-data';

export default LoDAdapter.extend({
  buildURL: function(type, id, record){
    id = null;
    record.id = id;
    return this._super(type, id, record) + record._attributes.lambda_instance_id + '/';
  },
  handleResponse: function(status, headers, payload) {
    if (this.isSuccess(status, headers, payload)) {
      return payload;
    }
    else{
      return new DS.InvalidError(payload.errors);
    }
  },
  updateRecord: function(store, type, snapshot) {
    var data = {};
    var serializer = store.serializerFor(type.modelName);

    serializer.serializeIntoHash(data, type, snapshot);

    var id = snapshot.id;
    var url = this.buildURL(type.modelName, id, snapshot, 'updateRecord');

    return this.ajax(url, "POST", { data: data });
  },
});
