import Ember from 'ember';

export default Ember.Component.extend({
  request : false,
  message : "",
  app_started: false,
  actions: {
    start(instance) {
      //send request to start instance
      instance.set('lambda_instance_id', this.get("instance-id"));
      instance.set('action', "start");
      instance.save();
      this.set("request", true);
      this.set("message", "Your request to start the lambda-instance was successfully sent to the server.");
      this.sendAction('action');
      return false;
    },
    stop(instance, apps) {
      var _this = this;
      //send request to stop instance
      apps.forEach(function(item) {
      if (item.get("started"))
      {
        _this.set("app_started", true);
      }
      });
      if (this.get("app_started")){
        if (confirm("There is a deployed application currently running on this lambda-instance.\nAre you sure you want to stop this lambda instance?")) {
            instance.set('lambda_instance_id', this.get("instance-id"));
            instance.set('action', "stop");
            instance.save();
            this.set("request", true);
            this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
            this.sendAction('action');
        }
      }
      else {
        instance.set('lambda_instance_id', this.get("instance-id"));
        instance.set('action', "stop");
        instance.save();
        this.set("request", true);
        this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
        this.sendAction('action');
        return false;
    }
    return false;
    },
  }
});
