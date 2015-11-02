import Ember from 'ember';

export default Ember.Component.extend({
  request: false,
  failure: false,
  message: "",
  actions: {
    start(app) {
      //send request to start application
      var _this = this;
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "start");
      app.save().then(
      function success() {
        _this.set("request", true);
        _this.set("message", "Your request to start the application was successfully sent to the server.");
        _this.sendAction('action');
      }).catch(
      function failure(reason) {
        app.set('errors', reason.errors);
        _this.set("failure", true);
      });
      return false;
    },
    stop(app) {
      //send request to stop application
      var _this = this;
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "stop");
      app.save().then(
      function success() {
        _this.set("request", true);
        _this.set("message", "Your request to stop the application was successfully sent to the server.");
        _this.sendAction('action');
      }).catch(
      function failure(reason) {
        app.set('errors', reason.errors);
        _this.set("failure", true);
      });
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
      this.sendAction('action', application_id, instance_id);
      return false;
    },
    withdraw(app) {
      var _this = this;
      //send request to withdraw application
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "withdraw");
      app.save().then(
      function success() {
        _this.set("request", true);
        _this.set("message", "Your request to undeploy the application was successfully sent to the server.");
        _this.sendAction('action');
      }).catch(
      function failure(reason) {
        app.set('errors', reason.errors);
        _this.set("failure", true);
      });
      return false;
    },
  },
});
