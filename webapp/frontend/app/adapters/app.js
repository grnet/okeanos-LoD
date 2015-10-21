import DS from "ember-data";
import ENV from 'frontend/config/environment';
import DataAdapterMixin from 'ember-simple-auth/mixins/data-adapter-mixin';

export default DS.JSONAPIAdapter.extend(DataAdapterMixin, {
  host: ENV.host + ':80',
  namespace: 'api',
  buildURL: function(type, id, record){
    console.log(record);
    return this._super(type, id, record) + "/" + record._attributes.application_id + '/' + record._attributes.call + "/";
  },
  authorizer: 'authorizer:django'
});
