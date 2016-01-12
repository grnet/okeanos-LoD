import DS from "ember-data";
import ENV from 'frontend/config/environment';

export default DS.JSONAPIAdapter.extend({
  host: ENV.host + ':443',
  namespace: 'api',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  },
  buildURL: function(type, id, record){
    return this._super(type, id, record) + '/';
  },
});
