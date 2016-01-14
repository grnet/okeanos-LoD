import Ember from 'ember';
import ENV from 'frontend/config/environment';

var Router = Ember.Router.extend({
  location: ENV.locationType,
});

Router.map(function () {
	this.route('lambda-instance');
	this.route('lambda-application');
	this.route('faqs', function() {
		this.route('lambda-instance', function() {
    		this.route('create');
    		this.route('start-stop');
    		this.route('kafka-topics');
		});

		this.route('lambda-application', function() {
			this.route('create');
			this.route('run');
			this.route('observe-running');
			this.route('check-running');
			this.route('view-results');
			this.route('export-data');
		});
    });
});

export default Router;
