import Ember from 'ember';
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  sortedInstances: Ember.computed.sort('instances', 'instanceSorting'),
  instanceSorting: ['name'],
  actions: {
    deploy(application_id) {
      if (!this.get("failure")) {
        var _this = this;
        Ember.run.later((function () {
          _this.set("request", false);
          _this.controllerFor('lambda-app').set('deployWait', true);
          _this.transitionToRoute('lambda-app', application_id);
        }), ENV.redirect_delay);
      }
    }
  }
});
