import Ember from "ember";

export default Ember.Controller.extend({
  actions: {
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-instance');
        _this.set("request", false);
      }), 2000);
    },
    start_stop: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
      }), 4000);
    },
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      alert.hidden=true;
    }
  },
});
