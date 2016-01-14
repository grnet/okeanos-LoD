import Ember from 'ember';
import ENV from 'frontend/config/environment';

var Router = Ember.Router.extend({
  location: ENV.locationType,
});

Router.map(function () {
	this.route('lambda-instance');
	this.route('lambda-application');
	this.route('faqs', function() {
    	this.route('create-lambda-instance');
    });
});

export default Router;
