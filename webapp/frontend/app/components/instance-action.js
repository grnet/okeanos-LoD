import Ember from 'ember';

export default Ember.Component.extend({
  request : false,
  message : "",
  actions: {
    start(instance) {
      //send request to start instance
      instance.set('lambda_instance_id', this.get("instance-id"));
      instance.set('action', "start");
      instance.save();
      this.set("request", true);
      this.set("message", "Your request to start the lambda-instance was successfully sent to the server.");
      return false;
    },
    stop(instance) {
      //send request to stop instance
      instance.set('lambda_instance_id', this.get("instance-id"));
      instance.set('action', "stop");
      instance.save();
      this.set("request", true);
      this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
      return false;
    },
  }
});
