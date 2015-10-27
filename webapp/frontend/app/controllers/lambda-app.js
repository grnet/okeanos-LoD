import Ember from "ember";

export default Ember.Controller.extend({
  actions: {
    withdraw: function()
    {
      var _this = this;
      Ember.run.later((function () {
        _this.store.unloadAll('lambda-instance');
      }), 2000);
    }
  }
});
