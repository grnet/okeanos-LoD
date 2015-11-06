import Ember from "ember";
import ENV from 'frontend/config/environment';

export default Ember.Controller.extend({
  failure: false,
  actions: {
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-instance');
        _this.set("request", false);
      }), ENV.message_dismiss);
    },
    start_stop: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
      }), ENV.message_dismiss);
    },
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      alert.hidden=true;
    }
  },
});
