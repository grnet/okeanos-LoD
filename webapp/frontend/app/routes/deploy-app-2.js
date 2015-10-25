import Ember from "ember";
import LoDRoute from 'frontend/routes/application';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

var ids;

export default LoDRoute.extend(AuthenticatedRouteMixin, {

  beforeModel: function () {
    this.store.unloadAll('lambda-app');
    this.store.unloadAll('app-action');
    let params = this.paramsFor(this.routeName);
    return this.store.findRecord('lambda-instance', params.instance_uuid);
  },

  model: function (params) {
    ids = this.store.peekAll('lambda-app').getEach('id');

    return Ember.RSVP.hash({
      instance: this.store.findRecord('lambda-instance', params.instance_uuid),
      applications: this.store.filter('lambda-app', {},
        function (application) {
          //if (application.get('status_code') !== 0) {
          //  return false;
          //}
          let id = application.get('id');
          for (var i = 0; i < ids.length; i++) {
            if (id === ids[i]) {
              return false;
            }
          }
          return true;
        }),
      app: this.store.createRecord('app-action', {})
    });
  },

  setupController: function (controller, model) {
    controller.set('applications', model.applications);
    controller.set('instance', model.instance);
    controller.set('app', model.app);
    controller.set('ids', ids);
  }

});
