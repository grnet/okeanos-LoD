import Ember from 'ember';
import ENV from 'frontend/config/environment';

var Router = Ember.Router.extend({
  location: ENV.locationType,
});

Router.map(function () {
  this.route('dashboard');
  this.route('lambda-instance');
  this.route('lambda-instance', {path: '/lambda-instances/:instance_uuid'});
  this.route('create-lambda-instance');
});

export default Router;
