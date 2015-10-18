import Ember from "ember";

var LoginController = Ember.Controller.extend({
  session: Ember.inject.service('session'),

  actions : {

    authenticate() {

      this.setProperties({
        loginFailed: false,
        serverError: false
      });
      let token = this.get("token");
      this.get('session').authenticate('authenticator:django', token).catch((xhr) => {
        console.debug('reason', xhr);
        if (xhr.statusText === 'UNAUTHORIZED') {
          this.set('loginFailed', true);
        }
        else {
          this.set('serverError', true);
        }
      });
    },

    dismiss: function(){
      Ember.$('#token').focus();
      Ember.$('#id_alert_wrongtoken > button').click();
      this.set('loginFailed', false);
      this.set("serverError", false);
    }
  }

});

export default LoginController;
