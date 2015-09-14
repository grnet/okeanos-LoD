
window.App.LoginController = Ember.Controller.extend({
  loginFailed: false,
  isProcessing: true,

actions : {
  login: function(options) {
  var _this = this;

    this.setProperties({
      loginFailed: false,
      isProcessing: true
    });

    App.token = token.value;

    var data = this.store.adapterFor('login').get('headers'),
    host = this.store.adapterFor('login').get('host'),
    namespace = this.store.adapterFor('login').namespace,
    postUrl = [ host, namespace ].join('/');

    $.ajax({
      url: postUrl,
      headers: {
          'Authorization':App.token
      },
      crossDomain: true,
      method: 'GET',
      dataType: 'json',
      data: data,
      xhrFields: {withCredentials: true},
      success: function(data, textStatus, jqXHR){
          _this.set("isProcessing", false);
          _this.set("loginFailed", false);
          _this.transitionToRoute('user.clusters');
      },
      error: function(data){
          _this.set("isProcessing", false);
          _this.set("loginFailed", true);
      }
    });
  },
  dismiss: function(){
    $('#token').focus();
    $('#id_alert_wrongtoken > button').click();
    this.set('loginFailed', false);
  }
}

});

export default window.App.LoginController;
