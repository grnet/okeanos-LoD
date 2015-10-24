import Ember from "ember";

export default Ember.Controller.extend({
  actions: {
    deploy() {
      var ids = this.get('ids');
      var instances;
      instances = this.store.filter('lambda-instance', {},
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
    }
  }
});
