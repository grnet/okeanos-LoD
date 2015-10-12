import Ember from "ember";

export default Ember.Controller.extend({

  types: [
    {type: "Stream"},
    {type: "Batch"}
  ],
  currentType: {
    type: "Stream"
  },

  actions : {
    upload: function() {
    var _this = this;

    var description = this.get("description");
    var type = this.get("type");
    var project_name = this.get("project_name");
    var file = this.get("file");
    var token = this.store.findRecord('user',1).token;

    var host = this.store.adapterFor('upload').get('host'),
    namespace = this.store.adapterFor('upload').namespace,
    postUrl = [ host, namespace ].join('/')
    headers = {'Authorization': "Token " + token};

    Ember.$.ajax({
      url: postUrl,
      headers: headers,
      crossDomain: true,
      method: 'POST',
      dataType: 'json',
      data: headers,
      xhrFields: {withCredentials: true},
      description: description,
      type: type,
      project_name: project_name,
      file: file,
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

    }
  }
});
