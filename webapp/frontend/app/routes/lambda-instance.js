import Ember from 'ember';
import LoDRoute from 'frontend/routes/application';
import ENV from 'frontend/config/environment';

export default LoDRoute.extend({

  model: function (params) {
    this.poll = Ember.run.later(this, function () {
      this.model(params).then(function () {
        this.modelFor('lambda-instance').instance.reload();
      }.bind(this));
    }, ENV.refresh_interval);

    return Ember.RSVP.hash({
      instance: this.store.findRecord('lambda-instance', params.instance_uuid),
      apps: this.store.peekAll('lambda-app')
    });

  },

  deactivate: function () {
    Ember.run.cancel(this.poll);
  }

});
