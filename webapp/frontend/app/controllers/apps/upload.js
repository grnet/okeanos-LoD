import Ember from "ember";

var UploadController = Ember.Controller.extend({
  session: Ember.inject.service('session'),

  actions : {
    upload: function() {

      var host = this.store.adapterFor('upload-app').get('host'),
      namespace = this.store.adapterFor('upload-app').namespace,
      postUrl = [ host, namespace ].join('/');
      const headers = {};

      this.get('session').authorize('authorizer:django', (headerName, headerValue) => {
      headers[headerName] = headerValue;
      });

      var data = new FormData(document.getElementById("upload-app-form"));

      var progress = document.getElementById('progress');
      var progress_text = document.getElementById('progress_text');
      progress.innerHTML =  '';
      progress.style.width = 0;
      progress_text.innerHTML = '';
      progress.className = "progress-bar progress-bar-striped active";


      Ember.$.ajax({
        url: postUrl,
        headers: headers,
        method: 'POST',
        processData: false,
        contentType: false,
        data: data,

        xhr: function()
        {
          var xhr = new window.XMLHttpRequest();
          //Upload progress
          xhr.upload.addEventListener("progress", function(evt){
            if (evt.lengthComputable) {
              var percentComplete = evt.loaded / evt.total;
              progress.style.width = percentComplete * 100 + '%';
              progress_text.innerHTML =  percentComplete * 100 + '%';
            }
          }, false);
          return xhr;
        },

        success: function(){
          progress.className = "progress-bar progress-bar-success";
          progress.innerHTML =  'Success.The application was uploaded successfully.';
        },
        statusCode: {
          400: function() {
            progress.className = "progress-bar progress-bar-danger";
            progress.innerHTML =  'Upload failed.<strong>The application with this name already exists.</strong> Please try another file.';
            progress_text.innerHTML =  '';
          }
        },
        error: function() {
          progress.className = "progress-bar progress-bar-danger";
          progress.innerHTML =  'Upload failed.<strong>Internal server error.</strong> Please try again later.';
          progress_text.innerHTML =  '';
        }
      });
    },
  },

});

export default UploadController;
