import Ember from 'ember';

export default Ember.Component.extend({
  request: false,
  failure: false,
  actions: {
    delete(lambdaApp) {
      if (confirm("Are you sure you want to delete?")) {
        var _this = this;
        lambdaApp.deleteRecord();
        lambdaApp.save().catch(function() {
          _this.failure = true;
        });
        return false;
        }
      return false;
    }
  }
});
