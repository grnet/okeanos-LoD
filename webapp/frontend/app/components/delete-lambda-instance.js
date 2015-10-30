import Ember from 'ember';

export default Ember.Component.extend({
  request: false,
  failure: false,
  actions: {
    delete(lambdaInstance) {
      var _this = this;
      if (confirm("Are you sure you want to delete?")) {
        lambdaInstance.deleteRecord();
        lambdaInstance.save().catch(function() {
          _this.failure = true;
        });
        // lambdaInstance.destroyRecord().catch(function() {
          // _this.set('failure', true);
        // });
        return false;
        }
      return false;
    }
  }
});
