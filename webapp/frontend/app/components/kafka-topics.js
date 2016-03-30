import Ember from 'ember';

export default Ember.Component.extend({
  topics: [],

  didInsertElement: function(){
    this._super(...arguments);

    // Initialize tokenfield.
    this.$('#tokenfield')
      .on('tokenfield:createtoken', this.createTokenEvent)
      .tokenfield({
        createTokensOnBlur: true
      });
  },

  createTokenEvent: function(event){
    var existingTokens = Ember.$(this).tokenfield('getTokens');

    Ember.$.each(existingTokens, function(index, token) {
      if (token.value === event.attrs.value){
        event.preventDefault();
      }
    });
  },

  actions: {
    updateTopics: function(){
      this.set('topics', this.$('#tokenfield').tokenfield('getTokensList').replace(/\s+/g, '').split(','));
    }
  }

});
