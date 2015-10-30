import Ember from 'ember';

export default Ember.Component.extend({
  request: false,
  failure: false,
  actions: {
    delete(lambdaApp) {
      if (confirm("Are you sure you want to delete?")) {
        lambdaApp.deleteRecord();
        lambdaApp.save().catch(function() {
          this.failure = true;
        });
        return false;
        }
      return false;
    }
  }
});
