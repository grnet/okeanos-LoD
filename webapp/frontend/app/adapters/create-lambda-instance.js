import Ember from 'ember';
import DS from 'ember-data';
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
  }),
  handleResponse: function(status, headers, payload) {
    if (this.isSuccess(status, headers, payload)) {
      return payload;
    }
    else{
      return new DS.InvalidError(payload.errors);
    }
  }
});

export default CreateLambdaInstanceAdapter;
