import Ember from "ember";

var UploadController = Ember.Controller.extend({

  actions : {
    upload: function() {
    var _this = this;

      this.setProperties({
        loginFailed: false,
        isProcessing: true
      });

      var token = this.get("token");

      //var data = this.store.adapterFor('login').get('headers'),
      var host = this.store.adapterFor('app').get('host'),
      namespace = this.store.adapterFor('app').namespace,
      postUrl = [ host, namespace ].join('/'),
      headers = {
        'Authorization': "Token " + "VtADuc3I2tTVlf5YrWM5QIM1-1tt0Xy2N6JRzeDWTM8",
        'Accept': "application/json",
        'Content-Type': "application/json"
      },
      type = "batch",
      description = this.get('description'),
      project_name = this.get('project_name'),
      file = this.get('file');

      var data = new FormData(document.getElementById("upload-app"));

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
          401: function() {
            console.log("401");
          }
        },
        error: function() {
          console.log("error");
        }
      });
    },
  },
  dismiss: function(){
    Ember.$('#id_alert_wrongtoken > button').click();
    this.set('sameUpload', false);
    this.set("serverError", false);
  }

});

export default UploadController;
