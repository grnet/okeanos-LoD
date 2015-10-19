import Ember from "ember";

export default Ember.Controller.extend({
  title: 'LoD Home',
  session: Ember.inject.service('session'),
  actions: {
    invalidateSession: function() {
      this.get('session').invalidate();
    }
  }
});
