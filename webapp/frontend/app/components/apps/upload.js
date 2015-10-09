export default Ember.Component.extend({
  willRender() {
    var token = this.store.peekRecord('user', 1);
    this.set(token, 'token');
  }
});
