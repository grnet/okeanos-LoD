import Ember from "ember";
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  actions: {
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      alert.hidden=true;
    },
    close_app_alert: function()
    {
      var alert = document.getElementById('app_alert');
      alert.hidden=true;
    },
    start_stop: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
        _this.set("app_request", false);
      }), ENV.message_dismiss);
    },
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-app');
        _this.set("request", false);
        _this.set("app_request", false);
      }), ENV.message_dismiss);
    },
  }
});
