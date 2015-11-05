import Ember from 'ember';
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  actions: {
    deploy(application_id, instance_id) {
      if (!this.get("failure")) {
        var _this = this;
        Ember.run.later((function () {
          _this.set("request", false);
          _this.transitionToRoute('lambda-instance', instance_id);
        }), ENV.redirect_delay);
      }
    }
  }
});
