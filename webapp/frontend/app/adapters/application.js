import DS from "ember-data";
import ENV from 'frontend/config/environment';

export default DS.JSONAPIAdapter.extend({
  host: ENV.host + ':80',
  namespace: 'api',
  headers: {
    'Authorization': "Token " + "12345678",
    'Accept': "application/json"
  },
  buildURL: function(type, id, record){
    return this._super(type, id, record) + '/';
  }
});
