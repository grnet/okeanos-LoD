import DS from "ember-data";
import ENV from 'frontend/config/environment';

export default DS.JSONAPIAdapter.extend({
  host: ENV.host + ':80',
  namespace: 'api',
  crossDomain: true,
  processData: false,
  contentType: false,
  headers: {
    'Authorization': "Token " + "VtADuc3I2tTVlf5YrWM5QIM1-1tt0Xy2N6JRzeDWTM8",
    'Accept': "application/json",
    'Content-Type': "multipart/form-data"
  }
 });
