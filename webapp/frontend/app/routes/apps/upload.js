import Ember from "ember";

var UploadRoute  = Ember.Route.extend({
  model() {
    return this.store.createRecord('app', {});
  }
});

export default UploadRoute;
