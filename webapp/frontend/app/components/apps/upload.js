import Ember from "ember";

const UploadComponent = Ember.Component.extend({



  actions : {
    upload: function() {
    //var _this = this;
    var store = this.store;

    //var token =  store.findRecord('user',1).token;

    var description = this.get("description");
    var type = this.get("type");
    var project_name = this.get("project_name");

    var file = this.$("input[name='file']")[0].value;

    store.createRecord('app', {
      project_name: project_name,
      file: file,
      type: type,
      description: description,
    });

    }
  }

});

export default UploadComponent;
