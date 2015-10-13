import DS from "ember-data";
import ENV from 'frontend/config/environment';

export default DS.JSONAPIAdapter.extend({
  host: ENV.host + ':80',
  namespace: 'api',
  headers: {
    'Authorization': "Token " + "12345678",
    'Accept': "application/json"
  }
});
