import Ember from "ember";

export default Ember.Controller.extend({
  actions: {
    deploy(application_id, instance_id) {
      var instances;
      var _this = this;
      Ember.run.later((function () {
        this.store.unloadAll('lambda-instance');
        this.modelFor('lambda-app').application.reload();
        let ids = this.store.peekAll('lambda-instance').getEach('id');
        instances = _this.store.filter('lambda-instance', {},
          function (li) {
            if (li.get('status_code') !== 0) {
              return false;
            }
            let id = li.get('id');
            for (var i = 0; i < ids.length; i++) {
              if (id === ids[i]) {
                return false;
              }
            }
            return true;
          });
      }), 1000);

      _this.set("request", true);
      Ember.run.later((function () {
        _this.set("request", false);
      }), 2500);
    }
  }
});
