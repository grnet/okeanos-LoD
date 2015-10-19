import Ember from 'ember';
import LoDRoute from 'frontend/routes/application';

export default LoDRoute.extend({
  model(params) {
    return Ember.RSVP.hash({
      instance: this.store.findRecord('lambda-instance', params.instance_uuid),
      apps: this.store.all('lambda-app')
    });
  }
});
