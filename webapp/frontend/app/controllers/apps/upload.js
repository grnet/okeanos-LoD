import Ember from "ember";

var UploadController = Ember.Controller.extend({
  sameUpload: false,
  serverError: false,
  successUpload: false,

  actions : {
    upload: function() {
    var _this = this;

      this.setProperties({
        loginFailed: false,
        isProcessing: true
      });

      var host = this.store.adapterFor('app').get('host'),
      namespace = this.store.adapterFor('app').namespace,
      postUrl = [ host, namespace ].join('/'),
      headers = {
        'Authorization': "Token " + "",
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
        },
        statusCode: {
          400: function() {
            _this.set('sameUpload', true);
            _this.set("serverError", false);
          }
        },
        error: function() {
          _this.set('sameUpload', false);
          _this.set("serverError", true);
        }
      });
    },
  },
  dismiss: function(){
    Ember.$('#upload-app').focus();
    Ember.$('#id_alert_wrongtoken > button').click();
    this.set('sameUpload', false);
    this.set("serverError", false);
  }

});

export default UploadController;
