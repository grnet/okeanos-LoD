import Ember from 'ember';

export default Ember.Route.extend({
  model(params) {
    return Ember.RSVP.hash({
      instance: this.store.findRecord('lambda-instance', params.instance_uuid),
      apps: this.store.all('lambda-app')
    });
  }
});
