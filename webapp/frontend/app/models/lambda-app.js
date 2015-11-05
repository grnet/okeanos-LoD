import DS from "ember-data";

// Information about lambda applications
var LambdaApp = DS.Model.extend({
  name: DS.attr(),
  path: DS.attr(),
  app_type: DS.attr(),
  description: DS.attr(),
  status_message: DS.attr(),
  status_code: DS.attr('number'),
  status_detail: DS.attr(),
  status_failure_message: DS.attr(),
  lambda_instances: DS.hasMany('lambda-instance'),
  started: DS.attr('boolean'),
  execution_environment_name: DS.attr()
});

export default LambdaApp;
