import Ember from "ember";

export default Ember.Controller.extend({
  actions: {
    deploy(application_id) {
      var ids = this.get('ids');
      ids.push(application_id);
      var applications;
      applications = this.store.filter('lambda-app', {},
        function (application) {
          //if (application.get('status_code') !== 0) {
          //  return false;
          //}
          let id = application.get('id');
          for (var i = 0; i < ids.length; i++) {
            if (id === ids[i]) {
              return false;
            }
          }
          return true;
        });
      var _this = this;
      _this.set("request", true);
      Ember.run.later((function () {
        _this.set("request", false);
      }), 2500);
    }
  }
});
