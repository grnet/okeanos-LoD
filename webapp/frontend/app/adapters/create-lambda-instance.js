import Ember from 'ember';
import GenericAdapter from 'frontend/adapters/application';

var CreateLambdaInstanceAdapter = GenericAdapter.extend({
  pathForType: function() {
    return 'lambda-instance';
  },
  headers: Ember.computed(function(){
    var defaultHeaders = GenericAdapter.create().get('headers');
    var newHeaders = Ember.$.extend(true, {}, defaultHeaders);

    newHeaders['Content-Type'] = "application/json";

    return newHeaders;
  })
});

export default CreateLambdaInstanceAdapter;
