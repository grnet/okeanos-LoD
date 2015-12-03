import Ember from "ember";

export default Ember.Controller.extend({
  enoughQuotas: false,
  actions: {
    saveLambdaInstance: function(newLambdaInstance){
      var self = this;
       newLambdaInstance.save().then(function(){
        self.transitionToRoute('lambda-instance', newLambdaInstance.get('id')).catch(function() {
          self.transitionToRoute('lambda-instances.index').then(function(newRoute) {
            newRoute.controller.set('message', 'Your lambda instance creation will begin shortly.');
            newRoute.controller.set('request', true);
            newRoute.controller.send('start_stop');
          });
        });
      });
    }
  }
});
