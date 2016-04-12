import Ember from 'ember';

export default Ember.Component.extend({
  request : false,
  message : "",
  app_started: false,
  failure: false,
  actions: {
    start(instance) {
      if (this.get('disabled')) {
        return false;
      }
      var _this = this;
      //send request to start instance
      var lambda_instance_id = this.get('instance-id');
      instance.set('lambda_instance_id', lambda_instance_id);
      instance.set('action', "start");
      instance.save().then(
      function success() {
        _this.set("request", true);
        _this.set("message", "Your request to start the lambda-instance was successfully sent to the server.");
        _this.sendAction('action', 'start', lambda_instance_id);
      }).catch(
      function failure() {
        _this.set("failure", true);
      });
      return false;
    },
    stop(instance, apps) {
      if (this.get('disabled')) {
        return false;
      }
      var _this = this;
      var lambda_instance_id = this.get('instance-id');
      if (this.get('check_apps'))
      {
        apps.forEach(function(item) {
        if (item.get("started"))
        {
          _this.set("app_started", true);
        }
        });
      }
      else if (this.get("started_app"))
      {
        this.set("app_started", true);
      }
      //send request to stop instance
      if (this.get("app_started")){
        if (confirm("There is a deployed application currently running on this lambda-instance.\nAre you sure you want to stop this lambda instance?")) {
            instance.set('lambda_instance_id', lambda_instance_id);
            instance.set('action', "stop");
            instance.save().then(
            function success() {
              _this.set("request", true);
              _this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
              _this.sendAction('action', 'stop', lambda_instance_id);
            }).catch(
            function failure() {
              _this.set("failure", true);
            });
        }
      }
      else {
        instance.set('lambda_instance_id', lambda_instance_id);
        instance.set('action', "stop");
        instance.save().then(
        function success() {
          _this.set("request", true);
          _this.set("message", "Your request to stop the lambda-instance was successfully sent to the server.");
          _this.sendAction('action', 'stop', lambda_instance_id);
        }).catch(
        function failure() {
          _this.set("failure", true);
        });
        return false;
    }
    return false;
    },
  }
});
