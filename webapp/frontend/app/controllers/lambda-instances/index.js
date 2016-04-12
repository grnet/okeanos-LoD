import Ember from 'ember';
import pagedArray from 'ember-cli-pagination/computed/paged-array';
import ENV from 'frontend/config/environment';

export default Ember.ArrayController.extend({
  success_delete: false,
  failed_delete: false,
  session: Ember.inject.service('session'),
  delete_success_message: '',
  delete_error_message: '',
  showFailed: false,
  queryParams: ["page", "perPage"],
  sortAscending: true,
  sortProperties: ['name'],

  instanceCount: Ember.computed('model.length', function() {
    return this.get('model.length');
  }),

  page: 1,
  perPage: 10,
  firstOfCurrentPage: Ember.computed('page', 'perPage', function() {
    if(this.get('model.length') === 0) {
      return 0;
    }
    else {
      return (this.get('page')-1)*(this.get('perPage'))+1;
    }
  }),
  lastOfCurrentPage: Ember.computed('page', 'perPage', 'instanceCount', function() {
    return Math.min(this.get('instanceCount'), (this.get('page'))*(this.get('perPage')));
  }),

  pagedContent: pagedArray('arrangedContent', {pageBinding: "page", perPageBinding: "perPage"}),

  totalPagesBinding: "pagedContent.totalPages",

  actions: {

    start_stop: function (action, instance_id)
    {
      var instance = this.get('model').findBy('id', instance_id);
      if (action === 'start') {
        instance.set('starting', true);
      }
      else if (action === 'stop') {
        instance.set('stopping', true);
      }
      var _this = this;
      Ember.run.later((function () {
        _this.set('request', false);
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

    delete_instance: function(instance_id) {
      var running_warning = "";
      if (this.get('model').findBy('id', instance_id).get('running_app')) {
        running_warning = " One or more application(s) are running on the instance.";
      }
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
            _this.get('model').findBy('id', instance_id).set('deleting', true);
            Ember.run.later((function () {
              _this.set('success_delete', false);
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

    close_alert: function()
    {
      var alert = document.getElementById('alert');
      alert.hidden=true;
      this.set('failed_delete', false);
    },

    checkPage: function () {
      Ember.run.once(this, function () {
        var page = this.get('page');
        var totalPages = this.get('totalPages');
        if (page > totalPages) {
          if (totalPages === 0) {
            totalPages = 1;
          }
          this.set('page', totalPages);
        }
        if (page <= 0 || isNaN(page)) {
          this.set('page', 1);
        }
      });
    },

  },
});
