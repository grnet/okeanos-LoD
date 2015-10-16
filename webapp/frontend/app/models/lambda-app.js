import DS from "ember-data";

// Information about lambda applications
var LambdaApp = DS.Model.extend({
  path: DS.attr(),
  app_type: DS.attr(),
  description: DS.attr(),
  status_message: DS.attr(),
  status_code: DS.attr('number'),
  status_detail: DS.attr(),
  lambda_instances: DS.hasMany('lambda-instance'),
  started: DS.attr('boolean')
});

export default LambdaApp;
