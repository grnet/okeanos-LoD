import Ember from "ember";

export default Ember.Controller.extend({
  actions: {
    withdraw: function()
    {
      this.store.unloadAll('lambda-instance');
    }
  }
});
