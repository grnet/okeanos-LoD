import Ember from "ember";
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  sortedApps: Ember.computed.sort('model.apps', 'applicationSorting'),
  applicationSorting: ['name'],
  session: Ember.inject.service('session'),
  failed_delete: false,
  success_delete: false,
  delete_success_message: '',
  delete_error_message: '',
  deployWait: false,
  deployID: -1,
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

    start_stop_instance: function (action)
    {
      var instance = this.get('model.instance');
      if (action === 'start') {
        instance.set('starting', true);
      }
      else if (action === 'stop') {
        instance.set('stopping', true);
      }
      var _this = this;
      Ember.run.later((function () {
        _this.set('request', false);
        _this.set('app_request', false);
      }), ENV.message_dismiss);
      Ember.run.later((function () {
        if (action === 'start') {
          instance.set('starting', false);
        }
        else if (action === 'stop') {
          instance.set('stopping', false);
        }
      }), ENV.button_delay);
    },

    start_stop_app: function (action, application_id)
    {
      var app = this.get('model.apps').findBy('id', application_id);
      if (action === 'start') {
        app.set('starting', true);
      }
      else if (action === 'stop') {
        app.set('stopping', true);
      }
      var _this = this;
      Ember.run.later((function () {
        _this.set('request', false);
        _this.set('app_request', false);
      }), ENV.message_dismiss);
      Ember.run.later((function () {
        if (action === 'start') {
          app.set('starting', false);
        }
        else if (action === 'stop') {
          app.set('stopping', false);
        }
      }), ENV.button_delay);
    },

    withdraw: function(application_id)
    {
      var app = this.get('model.apps').findBy('id', application_id);
      app.set('undeploying', true);
      var _this = this;
      Ember.run.later((function () {
        _this.store.find('lambda-app', application_id).then(function (application) {
          _this.store.unloadRecord(application);
        });
        _this.set('request', false);
        _this.set('app_request', false);
      }), ENV.message_dismiss);
    },

    delete_instance: function(instance_id) {
      var running_warning = "";
      this.get('model.apps').forEach(function (item) {
        if (item.get("started")) {
          running_warning = " One or more application(s) are running on the instance.";
        }
      });
      if (confirm("Are you sure you want to delete this lambda instance?" + running_warning)) {
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
            _this.set('success_delete', true);
            _this.set('delete_success_message', 'Your request to delete the lambda instance was successfully sent to the server.');
            _this.get('model.instance').set('deleting', true);
            Ember.run.later((function () {
              _this.set('success_delete', false);
              _this.transitionToRoute('dashboard');
            }), ENV.message_dismiss);
          },
          statusCode: {
            404: function(xhr) {
              _this.set('failed_delete', true);
              _this.set('delete_error_message', xhr.responseJSON.errors[0].detail);
            },
            409: function(xhr) {
              _this.set('failed_delete', true);
              _this.set('delete_error_message', xhr.responseJSON.errors[0].detail);
            }
          },
          error: function(xhr) {
            var error = 'Error ' + xhr.status + '. Your request to delete the instance was rejected. Please try again later or after the status of the instance has changed.';
            _this.set('failed_delete', true);
            _this.set('delete_error_message', error);
          }
        });
      }
    },

  }
});
