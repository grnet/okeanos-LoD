import Ember from 'ember';
import ENV from 'frontend/config/environment';

export default Ember.Route.extend({
  model: function(params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).reload();
    }, ENV.refresh_interval);

    return this.store.findAll('lambda-instance', params);
  }
});
