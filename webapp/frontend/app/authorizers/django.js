import Ember from 'ember';
import Base from 'ember-simple-auth/authorizers/base';

export default Base.extend({
  authorize: function(data, block) {
    if (!Ember.isEmpty(data.token)) {
      block('Authorization', 'Token ' + data.token);
    }
  }
});
