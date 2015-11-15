import Ember from 'ember';
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  sortedApps: Ember.computed.sort('applications', 'applicationSorting'),
  applicationSorting: ['name'],
  actions: {
    deploy(application_id) {
      if (!this.get("failure")) {
        var _this = this;
        Ember.run.later((function () {
          _this.set("request", false);
          _this.transitionToRoute('lambda-app', application_id);
        }), ENV.redirect_delay);
      }
    }
  }
});
