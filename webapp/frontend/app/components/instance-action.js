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
      if (this.get("verify"))
      {
        apps.forEach(function(item) {
          if (item.get("started"))
          {
            _this.set("app_started", true);
          }
        });
        if (this.get("app_started")){
          this.sendAction('action', true);
          return false;
        }
        else {
          instance.set('lambda_instance_id', this.get("instance-id"));
          instance.set('action', "stop");
          instance.save();
          this.set("request", true);
          this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
          this.sendAction('action', false);
          return false;
        }
      }
      else {
        instance.set('lambda_instance_id', this.get("instance-id"));
        instance.set('action', "stop");
        instance.save();
        this.set("request", true);
        this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
        this.sendAction('action');
      }
      return false;
    },
  }
});
