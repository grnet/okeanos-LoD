import Ember from "ember";

export default Ember.Controller.extend({
  verify: true,
  confirm: false,
  actions: {
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      alert.hidden=true;
    },
    start_stop: function()
    {
      this.set("confirm", false);
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
        _this.set("app_request", false);
      }), 4000);
    },
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-app');
        _this.set("request", false);
      }), 3000);
    },
  }
});
