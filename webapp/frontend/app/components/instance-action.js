import Ember from 'ember';

export default Ember.Component.extend({
  request : false,
  message : "",
  actions: {
    start(instance) {
      //send request to start instance
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('action', "start");
      app.save();
      this.set("request", true);
      this.set("message", "Your request to start the lambda-instance was successfully sent to the server.");
      return false;
    },
    stop(instance) {
      //send request to stop instance
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('action', "stop");
      app.save();
      this.set("request", true);
      this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
      return false;
    },
  }
});
