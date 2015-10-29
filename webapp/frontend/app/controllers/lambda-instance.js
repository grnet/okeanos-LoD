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
      }), 4000);
    },
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-instance');
        _this.set("request", false);
      }), 3000);
    },
    verify: function(started_app)
    {
      if (started_app)
      {
        var con = window.confirm("There is a deployed application currently running on this lambda-instance.\nIf you want to stop it press ok and then press again the STOP button.");
        if (con)
        {
          this.set("verify", false);
          this.set("confirm", true);
        }
        else{
          this.set("verify", true);
        }
    }
    else {
      this.set("confirm", false);
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
      }), 4000);
    }
  },
  }
});
