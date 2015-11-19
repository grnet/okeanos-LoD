import Ember from 'ember';
import pagedArray from 'ember-cli-pagination/computed/paged-array';
import ENV from 'frontend/config/environment';

export default Ember.ArrayController.extend({
  success_delete: false,
  failed_delete: false,
  delete_success_message: '',
  delete_error_message: '',
  error: false,
  session: Ember.inject.service('session'),
  queryParams: ["page", "perPage"],
  sortProperties: ['name'],
  sortAscending: true,

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

  actions:{
    delete_app: function(app_id) {
      if (this.get('model').findBy('id', app_id).get('deployed')) {
        if (confirm("The application is deployed on one or more lambda-instance(s).\n" +
            "Please undeploy it before deleting. Click 'OK' to be navigated to the application details page.")) {
          this.transitionToRoute('lambda-app', app_id);
        }
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
              _this.set('success_delete', true);
              _this.set('delete_success_message', 'Your request to delete the application was successfully sent to the server.');
              Ember.run.later((function () {
                _this.store.find('lambda-app', app_id).then(function (application) {
                  _this.store.unloadRecord(application);
                });
                _this.set('success_delete', false);
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
