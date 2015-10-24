import Ember from 'ember';
import ENV from 'frontend/config/environment';

var Router = Ember.Router.extend({
  location: ENV.locationType,
});

Router.map(function () {
  this.route('dashboard');
  this.resource('lambda-instances', function() {
  });
  this.route('lambda-instance', {path: '/lambda-instance/:instance_uuid'});
  this.route('create-lambda-instance');
  this.route('lambda-app', {path: '/apps'});
  this.route('lambda-app', {path: '/apps/:app_uuid'});
  this.route('deploy-app-1', {path: '/apps/:app_uuid/deploy'});
  this.route('deploy-app-2', {path: '/lambda-instance/:instance_uuid/deploy'});
  this.resource('lambda-apps', function() {
    this.route('upload');
  });
  this.route('lambda-app', {path: '/apps/:app_uuid'});
});

export default Router;
