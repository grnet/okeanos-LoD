import Ember from "ember";
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  sortedInstances: Ember.computed.sort('model.instances', 'instanceSorting'),
  instanceSorting: ['name'],
  failure: false,
  session: Ember.inject.service('session'),
  failed_delete: false,
  success_delete: false,
  delete_success_message: '',
  delete_error_message: '',
  actions: {
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-instance');
        _this.set('request', false);
      }), ENV.message_dismiss);
    },
    start_stop: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.set('request', false);
      }), ENV.message_dismiss);
    },
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      this.set('failed_delete', false);
      alert.hidden=true;
    },
    delete_app: function(app_id) {
      if (this.get('model.instances.length')) {
        alert("The application is deployed on one or more lambda-instance(s).\nPlease undeploy it before deleting.");
      }
      else {
        if (confirm("Are you sure you want to delete this application?")) {
          var _this = this;

          var host = this.store.adapterFor('upload-app').get('host'),
            namespace = this.store.adapterFor('upload-app').namespace,
            postUrl = [host, namespace].join('/');
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
            success: function () {
              _this.store.unloadAll('lambda-app');
              _this.set('delete_success_message', 'Your request to delete the application was successfully sent to the server.');
              _this.set('success_delete', true);
              Ember.run.later((function () {
                _this.set('success_delete', false);
                _this.transitionToRoute('dashboard');
              }), ENV.message_dismiss);
            },
            statusCode: {
              404: function (xhr) {
                _this.set('failed_delete', true);
                _this.set('delete_error_message', xhr.responseJSON.errors[0].detail);
              },
              409: function (xhr) {
                _this.set('failed_delete', true);
                _this.set('delete_error_message', xhr.responseJSON.errors[0].detail);
              }
            },
            error: function (xhr) {
              var error = 'Error ' + xhr.status + '. Your request to delete the application was rejected. Please try again later or after the status of the instance has changed.';
              _this.set('failed_delete', true);
              _this.set('delete_error_message', error);
            }
          });
        }
      }
    },
  },
});
