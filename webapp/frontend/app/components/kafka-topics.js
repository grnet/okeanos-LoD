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

    var duplicate = false;
    Ember.$.each(existingTokens, function(index, token) {
      if (token.value === event.attrs.value){
        duplicate = true;

        return false;
      }

      return true;
    });

    // If the provided name for the new token already exists, delete the input text
    if(duplicate){
      var componentId = Ember.$(this)[0].id;
      Ember.$('#' + componentId + " #" + componentId + "-tokenfield")[0].value = "";
    }

    return !duplicate;
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
