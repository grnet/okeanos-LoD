import DS from "ember-data";
import Env from 'frontend/config/environment';

var CreateLambdaInstanceAdapter = DS.JSONAPIAdapter.extend({
  host: Env.host,
  namespace: 'api',
  pathForType: function(type) {
    return 'lambda-instance';
  },
  headers: {
    'Authorization': "Token " + Env.token,
    'Accept': "application/json",
    'Content-Type': "application/json"
  }
});

export default CreateLambdaInstanceAdapter; 