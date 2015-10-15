import Ember from "ember";

var UploadController = Ember.Controller.extend({
  sameUpload: false,
  serverError: false,
  successUpload: false,

  actions : {
    upload: function() {
    var _this = this;

      this.setProperties({
        sameUpload: false,
        serverError: false,
        successUpload: false,
      });

      var host = this.store.adapterFor('app').get('host'),
      namespace = this.store.adapterFor('app').namespace,
      postUrl = [ host, namespace ].join('/'),
      headers = {
        'Authorization': "Token " + "VtADuc3I2tTVlf5YrWM5QIM1-1tt0Xy2N6JRzeDWTM8",
        'Accept': "application/json",
      };

      var data = new FormData(document.getElementById("upload-app-form"));

      Ember.$.ajax({
        url: postUrl,
        headers: headers,
        method: 'POST',
        processData: false,
        contentType: false,
        data: data,
        success: function(){
          console.log("success");
          _this.set("successUpload", true);
          _this.set("sameUpload", false);
          _this.set("serverError", false);
        },
        statusCode: {
          400: function() {
            _this.set("sameUpload", true);
            _this.set("serverError", false);
            _this.set("successUpload", false);
          }
        },
        error: function() {
          _this.set("sameUpload", false);
          _this.set("serverError", true);
          _this.set("successUpload", false);
        }
      });
    },
  },

});

export default UploadController;
