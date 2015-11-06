import Ember from "ember";
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  failure: false,
  session: Ember.inject.service('session'),
  failed_delete: false,
  success_delete: false,
  message: '',
  actions: {
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-instance');
        _this.set("request", false);
      }), ENV.message_dismiss);
    },
    start_stop: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
      }), ENV.message_dismiss);
    },
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      this.set('failed_delete', false);
      alert.hidden=true;
    },
    delete_app: function(app_id) {
      if (confirm("Are you sure you want to delete this application?")) {
        var _this = this;

        var host = this.store.adapterFor('upload-app').get('host'),
        namespace = this.store.adapterFor('upload-app').namespace,
        postUrl = [ host, namespace].join('/');
        postUrl = postUrl + app_id + '/';
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
            _this.store.unloadAll('lambda-app');
            _this.set('message', 'Your request to delete the application was successfully sent to the server.');
            _this.set("success_delete", true);
            Ember.run.later((function () {
              _this.set("success_delete", false);
              _this.transitionToRoute('dashboard');
            }), 3000);
          },
          statusCode: {
            500: function() {
              _this.set('failed_delete', true);
              _this.set('message', "Your request to delete the application was rejected.Please try again later when the status of the instance has changed.");
            }
          },
          error: function(response) {
            _this.set('failed_delete', true);
            _this.set('message', response.responseJSON.errors[0].detail);
          }
        });
      }
    },
  },
});
