import Ember from 'ember';

export default Ember.Component.extend({
  request: false,
  failure: false,
  message: "",
  actions: {
    start(app) {
      //send request to start application
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "start");
      app.save();
      this.set("request", true);
      this.set("message", "Your request to start the application was successfully sent to the server.");
      return false;
    },
    stop(app) {
      //send request to stop application
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "stop");
      app.save();
      this.set("request", true);
      this.set("message", "Your request to stop the application was successfully sent to the server.");
      return false;
    },
    deploy(app) {
      //send request to deploy application
      let application_id = this.get('application-id');
      let instance_id = this.get('instance-id');
      app.set('application_id', application_id);
      app.set('lambda_instance_id', instance_id);
      app.set('call', "deploy");
      var _this = this;
      app.save().catch(function() {
        _this.set('failure', true);
      });
      //this.set("request", true);
      //this.set("message", "Your request to deploy the application was successfully sent to the server.");
      this.sendAction('action', application_id, instance_id);
      return false;
    },
    withdraw(app) {
      //send request to withdraw application
      if (this.get("started")){
        window.alert("You cannot withdraw the application from this lambda-instance because it is currently running.")
      }
      else {
        app.set('application_id', this.get("application-id"));
        app.set('lambda_instance_id', this.get("instance-id"));
        app.set('call', "withdraw");
        app.save();
        this.set("request", true);
        this.set("message", "Your request to withdraw the application was successfully sent to the server.");
      }
      return false;
    }
  }
});
