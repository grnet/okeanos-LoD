import Ember from "ember";

var UploadController = Ember.Controller.extend({
  session: Ember.inject.service('session'),
  wrongExt: false,

  actions : {
    upload: function() {

      this.setProperties({
        wrongExt: false,
      });

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
      var progress_bar = document.getElementById('progress_bar');
      progress.innerHTML =  '';
      progress.style.width = 0;
      progress_text.innerHTML = '';
      progress.className = "progress-bar progress-bar-striped active";
      progress_bar.hidden=true;

      var res = this.get("file").split(".");
      var ext = res[res.length-1];
      if (ext != "jar")
      {
        this.set("wrongExt", true);
      }
      else {
      progress_bar.hidden=false;
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
              progress_text.innerHTML =  Math.floor(percentComplete * 100) + '%';
            }
          }, false);
          return xhr;
        },

        success: function(){
          progress.className = "progress-bar progress-bar-success";
          progress.innerHTML =  'Success.Your request to upload the application has been sent.';
        },
        statusCode: {
          400: function() {
            progress.className = "progress-bar progress-bar-danger";
            progress.innerHTML =  'Failure. Your request to upload the application has failed.Try another application';
            progress_text.innerHTML =  '';
          }
        },
        error: function() {
          progress.className = "progress-bar progress-bar-danger";
          progress.innerHTML =  'Your request to application the file has been rejected.Please try again later.';
          progress_text.innerHTML =  '';
        }
      });
      }
    },
  },

});

export default UploadController;
