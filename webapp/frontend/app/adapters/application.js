import DS from "ember-data";
import ENV from 'frontend/config/environment';
import DataAdapterMixin from 'ember-simple-auth/mixins/data-adapter-mixin';

export default DS.JSONAPIAdapter.extend(DataAdapterMixin, {
  host: ENV.host + ':80',
  namespace: '/api',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  buildURL: function(type, id, record){
    return this._super(type, id, record) + '/';
  },
  authorizer: 'authorizer:django'
});
