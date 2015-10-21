import Ember from 'ember';

export default Ember.Component.extend({
  actions: {
    start(app) {
      //send request to start application
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.save();

      return false;
    },
  }
});
