import Ember from "ember";

export default Ember.Controller.extend({
  actions: {
    saveLambdaInstance: function(newLambdaInstance){
      var self = this;
       newLambdaInstance.save().then(function(){
        self.transitionToRoute('lambda-instance', newLambdaInstance.get('id'));
      });
    }
  }
});
