import Ember from "ember";

var ClustersController = Ember.Controller.extend({

  actions : {
    list: function() {
    var _this = this;

    var token = this.get("token");

    var host = this.store.adapterFor('clusters').get('host'),
    namespace = this.store.adapterFor('clusters').namespace,
    postUrl = [ host, namespace ].join('/'),
    headers = {'Authorization': "Token " + token};


    Ember.$.ajax({
      url: postUrl,
      headers: headers,
      crossDomain: true,
      method: 'GET',
      dataType: 'json',
      data: headers,
      xhrFields: {withCredentials: true},
      success: function(){
          console.log("success");
      },
      error: function() {
        console.log("error");
      }
    });
  },
  uploadApp: function() {
      this.transitionToRoute('apps.upload');
  }
}


});

export default ClustersController;
