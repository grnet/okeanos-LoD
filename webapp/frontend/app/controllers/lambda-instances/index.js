import Ember from 'ember';
import pagedArray from 'ember-cli-pagination/computed/paged-array';
import ENV from 'frontend/config/environment';

export default Ember.ArrayController.extend({
  success_delete: false,
  failed_delete: false,
  session: Ember.inject.service('session'),
  message: '',
  queryParams: ["page", "perPage"],
  sortAscending: true,
  sortProperties: ['name'],

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
  lastOfCurrentPage: Ember.computed('page', 'perPage', 'content', function() {
    return Math.min(this.get('content.length'), (this.get('page'))*(this.get('perPage')));
  }),

  pagedContent: pagedArray('arrangedContent', {pageBinding: "page", perPageBinding: "perPage"}),

  totalPagesBinding: "pagedContent.totalPages",

  actions: {

    start_stop: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
      }), ENV.message_dismiss);
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
            }), 4000);
          },
          statusCode: {
            404: function(xhr) {
              _this.set('failed_delete', true);
              _this.set('message', xhr.responseJSON.errors[0].detail);
            },
            409: function(xhr) {
              _this.set('failed_delete', true);
              _this.set('message', xhr.responseJSON.errors[0].detail);
            }
          },
          error: function(xhr) {
            var error = 'Error ' + xhr.status + '. Your request to delete the instance was rejected. Please try again later or after the status of the instance has changed.';
            _this.set('failed_delete', true);
            _this.set('message', error);
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
  },
});
