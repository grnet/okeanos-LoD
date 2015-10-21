import Ember from 'ember';
import ENV from 'frontend/config/environment';

var Router = Ember.Router.extend({
  location: ENV.locationType,
});

Router.map(function () {
  this.route('dashboard');
  this.resource('lambda-instances', function() {
  });
  this.resource('lambda-instance', {path: '/lambda-instance/:instance_uuid'});
  this.route('create-lambda-instance');
  this.route('lambda-app', {path: '/apps'});
  this.route('lambda-app', {path: '/apps/:app_uuid'});
});

export default Router;
