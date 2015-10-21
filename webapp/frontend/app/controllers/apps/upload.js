import Ember from "ember";

var UploadController = Ember.Controller.extend({
  sameUpload: false,
  serverError: false,
  successUpload: false,
  noFile: false,
  session: Ember.inject.service('session'),

  actions : {
    upload: function() {
    var _this = this;

      this.setProperties({
        sameUpload: false,
        serverError: false,
        successUpload: false,
        noFile: false,
      });

      var host = this.store.adapterFor('upload-app').get('host'),
      namespace = this.store.adapterFor('upload-app').namespace,
      postUrl = [ host, namespace ].join('/');
      const headers = {};

      var file = this.get("file");
      if (file == null)
      {
        this.set("noFile", false);
      }
      console.log(file);

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
              //Do something with upload progress
              console.log(percentComplete);
              progress.style.width = percentComplete * 100 + '%';
              progress_text.innerHTML =  percentComplete * 100 + '%';
            }
          }, false);
          return xhr;
        },

        success: function(){
          console.log("success");
          _this.set("successUpload", true);
          _this.set("sameUpload", false);
          _this.set("serverError", false);
          progress.className = "progress-bar progress-bar-success";
          progress.innerHTML =  'Success';
        },
        statusCode: {
          400: function() {
            _this.set("sameUpload", true);
            _this.set("serverError", false);
            _this.set("successUpload", false);
            progress.className = "progress-bar progress-bar-danger";
            progress.innerHTML =  'Failed';
            progress_text.innerHTML =  '';
          }
        },
        error: function() {
          _this.set("sameUpload", false);
          _this.set("serverError", true);
          _this.set("successUpload", false);
          progress.className = "progress-bar progress-bar-danger";
          progress.innerHTML =  'Failed';
          progress_text.innerHTML =  '';
        }
      });
    },
  },

});

export default UploadController;
