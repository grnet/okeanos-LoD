import Ember from "ember";

export default Ember.Controller.extend({
  session: Ember.inject.service('session'),
  failed_delete: false,
  success_delete: false,
  message: '',
  actions: {
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      alert.hidden=true;
      this.set('failed_delete', false);
    },
    close_app_alert: function()
    {
      var alert = document.getElementById('app_alert');
      alert.hidden=true;
    },
    start_stop: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
        _this.set("app_request", false);
      }), 4000);
    },
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-app');
        _this.set("request", false);
        _this.set("app_request", false);
      }), 3000);
    },
    delete_instance: function(instance_id) {
      if (confirm("Are you sure you want to delete this lambda instance?")) {
        var _this = this;

        var host = this.store.adapterFor('upload-app').get('host'),
        postUrl = host + '/api/lambda-instances/' + instance_id + '/';
        const headers = {};

        this.get('session').authorize('authorizer:django', (headerName, headerValue) => {
        headers[headerName] = headerValue;
        });

        Ember.$.ajax({
          url: postUrl,
          headers: headers,
          method: 'DELETE',
          processData: false,
          contentType: false,
          success: function(){
            _this.store.unloadAll('lambda-instance');
            _this.set('success_delete', true);
            _this.set('message', 'Your request to delete the lambda instance was successfully sent to the server.');
            Ember.run.later((function () {
              _this.set("success_delete", false);
              _this.transitionToRoute('lambda-instances');
            }), 3000);
          },
          statusCode: {
            500: function() {
              _this.set('failed_delete', true);
              _this.set('message', "Your request to delete the instance was rejected.Please try again later when the status of the instance has changed.");
            }
          },
          error: function(response) {
            _this.set('failed_delete', true);
            _this.set('message', response.responseJSON.errors[0].detail);
          }
        });
      }
    },
  }
});
