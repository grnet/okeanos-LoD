import Ember from 'ember';

export default Ember.Component.extend({
  request: false,
  failure: false,
  message: "",
  actions: {
    start(app) {
      if (this.get('disabled')) {
        return false;
      }
      //send request to start application
      var _this = this;
      var application_id = this.get('application-id');
      var instance_id = this.get('instance-id');
      app.set('application_id', application_id);
      app.set('lambda_instance_id', instance_id);
      app.set('call', "start");
      app.save().then(
      function success() {
        _this.set("request", true);
        _this.set("message", "Your request to start the application was successfully sent to the server.");
        _this.sendAction('action', 'start', application_id, instance_id);
      }).catch(
      function failure() {
        _this.set("failure", true);
      });
      return false;
    },
    stop(app) {
      if (this.get('disabled')) {
        return false;
      }
      //send request to stop application
      var _this = this;
      var application_id = this.get('application-id');
      var instance_id = this.get('instance-id');
      app.set('application_id', application_id);
      app.set('lambda_instance_id', instance_id);
      app.set('call', "stop");
      app.save().then(
      function success() {
        _this.set("request", true);
        _this.set("message", "Your request to stop the application was successfully sent to the server.");
        _this.sendAction('action', 'stop', application_id, instance_id);
      }).catch(
      function failure() {
        _this.set("failure", true);
      });
      return false;
    },
    deploy(app) {
      //send request to deploy application
      let application_id = this.get('application-id');
      let instance_id = this.get('instance-id');
      var _this = this;
      app.set('application_id', application_id);
      app.set('lambda_instance_id', instance_id);
      app.set('call', "deploy");
      app.save().then(
        function success() {
          _this.set("request", true);
          _this.set("message", "Your request to deploy the application was successfully sent to the server.");
          _this.sendAction('action', application_id, instance_id);
        }).catch(
        function () {
          _this.set('failure', true);
        });
      return false;
    },
    withdraw(app) {
      if (this.get('disabled')) {
        return false;
      }
      var _this = this;
      //send request to withdraw application
      let application_id = this.get('application-id');
      let instance_id = this.get('instance-id');
      app.set('application_id', application_id);
      app.set('lambda_instance_id', instance_id);
      app.set('call', "withdraw");
      app.save().then(
      function success() {
        _this.set("request", true);
        _this.set("message", "Your request to undeploy the application was successfully sent to the server.");
        _this.sendAction('action', application_id, instance_id);
      }).catch(
      function failure() {
        _this.set("failure", true);
      });
      return false;
    },
  },
});
