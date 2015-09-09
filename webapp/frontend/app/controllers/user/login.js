
window.App.LoginController = Ember.Controller.extend({
  loginFailed: false,
  isProcessing: false,

actions : {
  login: function(options) {

    this.setProperties({
      loginFailed: false,
      isProcessing: true
    });

    console.log(token.value);
    App.token = token.value;

    var data = this.store.adapterFor('login').get('headers'),
    host = this.store.adapterFor('login').get('host'),
    namespace = this.store.adapterFor('login').namespace,
    postUrl = [ host, namespace ].join('/');

    $.ajax({
      url: postUrl,
      headers: {
          'Authorization':App.token,
          'Access-Control-Allow-Origin': '*'
      },
      crossDomain: true,
      method: 'GET',
      dataType: 'json',
      data: data,
      xhrFields: {withCredentials: true},
      success: function(data){
        console.log('succes: '+data);
      }
    });

    $.ajax({
      url: postUrl,
      headers:{"Authorization":App.token}
    });/*.then(function() {
      this.set("isProcessing", false);
      document.location = "/welcome";
    }.bind(this), function() {
      this.set("isProcessing", false);
      this.set("loginFailed", true);
    }.bind(this));*/


/*
    return new Ember.RSVP.Promise((resolve, reject) => {
        Ember.$.ajax({
            crossOrigin: true,
            url: host,
            type: 'GET',
            headers:{'Authorization': App.token}
        }).then(function(response) {
            Ember.run(function() {
                resolve({
                    token: response.id_token
                });
            });
        }, function(xhr, status, error) {
            var response = xhr.responseText;
            Ember.run(function() {
                reject(response);
            });
        });
    });
*/

  },
  dismiss: function(){
    $('#token').focus();
    $('#id_alert_wrongtoken > button').click();
    this.set('loginFailed', false);
  }
}

});

export default window.App.LoginController;
