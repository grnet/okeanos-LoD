import Ember from "ember";
import LoDRoute from 'frontend/routes/application';
import AuthenticatedRouteMixin from 'ember-simple-auth/mixins/authenticated-route-mixin';

var ids;

export default LoDRoute.extend(AuthenticatedRouteMixin, {

  beforeModel: function () {
    this.store.unloadAll('lambda-instance');
    this.store.unloadAll('app-action');
    let params = this.paramsFor(this.routeName);
    return this.store.findRecord('lambda-app', params.app_uuid);
  },

  model: function (params) {
    ids = this.store.peekAll('lambda-instance').getEach('id');

    return Ember.RSVP.hash({
      application: this.store.findRecord('lambda-app', params.app_uuid),
      instances: this.store.filter('lambda-instance', {},
        function (li) {
          if (li.get('status_code') !== 0) {
            return false;
          }
          let id = li.get('id');
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
    controller.set('application', model.application);
    controller.set('instances', model.instances);
    controller.set('app', model.app);
    controller.set('ids', ids);
  }

});
