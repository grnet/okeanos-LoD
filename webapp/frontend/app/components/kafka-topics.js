import Ember from 'ember';

export default Ember.Component.extend({
  topics: [],

  id: "",

  didInsertElement: function(){
    this._super(...arguments);

    // Initialize tokenfield.
    this.$('#' + this.get('id'))
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
      var tokenList = this.$('#' + this.get('id')).tokenfield('getTokensList', ',', false, false);

      if (tokenList === "") {
        this.set('topics', []);
      }
      else{
        this.set('topics', tokenList.split(','));
      }
    }
  }

});
