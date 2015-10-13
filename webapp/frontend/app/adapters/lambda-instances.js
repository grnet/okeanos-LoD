import DS from "ember-data";
import config from 'frontend/config/environment';

export default DS.JSONAPIAdapter.extend({
  host: config.host + ':80',
  namespace: 'api/',
  headers: {
    'Authorization': "Token " + '',
    'Accept': 'application/json'
  }
});
