import Ember from "ember";

var UploadController = Ember.Controller.extend({
  sameUpload: false,
  serverError: false,
  successUpload: false,
  session: Ember.inject.service('session'),

  actions : {
    upload: function() {
    var _this = this;

      this.setProperties({
        sameUpload: false,
        serverError: false,
        successUpload: false,
      });

      var host = this.store.adapterFor('upload-app').get('host'),
      namespace = this.store.adapterFor('upload-app').namespace,
      postUrl = [ host, namespace ].join('/');
      const headers = {};

      this.get('session').authorize('authorizer:django', (headerName, headerValue) => {
      headers[headerName] = headerValue;
      //Ember.$.ajax('/secret-data', { headers });
      });

      var data = new FormData(document.getElementById("upload-app-form"));

      var progress = document.getElementById('progress');
      var progress_text = document.getElementById('progress_text');
      progress.style.width = 0;


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
          //progress.style.width = 0 + '%';
        },
        statusCode: {
          400: function() {
            _this.set("sameUpload", true);
            _this.set("serverError", false);
            _this.set("successUpload", false);
            //progress.style.width = 0 + '%';
          }
        },
        error: function() {
          _this.set("sameUpload", false);
          _this.set("serverError", true);
          _this.set("successUpload", false);
          //progress.style.width = 0 + '%';
        }
      });
    },
  },

});

export default UploadController;
