import Ember from 'ember';

export default Ember.Component.extend({

  didInsertElement: function() {
    if ((this.$("#title").text() == " Title" || this.$("#title").text() == "") &&
    	(this.$("#message").text() == "Message" || this.$("#message").text() == "")){
    	this.$(".content").css('display', 'none');
    }
  },

});
