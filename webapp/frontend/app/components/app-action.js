import Ember from 'ember';

export default Ember.Component.extend({
  request : false,
  actions: {
    start(app) {
      //send request to start application
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "start");
      app.save();
      this.set("request", true);
      return false;
    },
    stop(app) {
      //send request to stop application
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "stop");
      app.save();
      this.set("request", true);
      return false;
    },
    deploy(app) {
      //send request to deploy application
      app.set('application_id', this.get("application-id"));
      app.set('lambda_instance_id', this.get("instance-id"));
      app.set('call', "deploy");
      app.save();
      this.set("request", true);
      return false;
    },
  }
});
