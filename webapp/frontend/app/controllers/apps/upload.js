import Ember from "ember";

export default Ember.Controller.extend({

  types: [
    {type: "streaming"},
    {type: "batch"}
  ],
  currentType: {
    type: "streaming"
  },
/*
  actions : {
    upload: function() {
    //var _this = this;
    var store = this.store;

    //var token =  store.findRecord('user',1).token;

    var host = this.store.adapterFor('app').get('host'),
    namespace = "api/apps/",
    postUrl = [ host, namespace ].join('/'),
    headers = {'Authorization': "Token VtADuc3I2tTVlf5YrWM5QIM1-1tt0Xy2N6JRzeDWTM8"};

    var description = this.get("description");
    var type = this.get("type");
    var project_name = this.get("project_name");

    var data = new FormData();
    data.append( 'file', $('#file')[0].files[0] );
    data.append( 'type', type);
    data.append( 'project_name', project_name);
    data.append( 'description', description);

    var file = this.$("input[name='file']")[0].value;

    store.createRecord('app', {
      project_name: project_name,
      file: file,
      type: type,
      description: description,
    });



    Ember.$.ajax({
      url: postUrl,
      headers: headers,
      crossDomain: true,
      method: 'POST',
      data: data,
      processData: false,
      contentType: false,
      xhrFields: {withCredentials: true},
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
  } */
});
