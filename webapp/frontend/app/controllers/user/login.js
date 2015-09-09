
window.App.LoginController = Ember.Controller.extend({
  loginFailed: false,
  isProcessing: false,

actions : {
  login: function(options) {
    var _this = this;
    var adapter = this.container.lookup('adapter:login');

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

    /*
    adapter.ajax(response, 'GET').then(function() {
      _this.set("isProcessing", false);
      document.location = "/welcome";
    }.bind(this), function() {
      _this.set("isProcessing", false);
      _this.set("loginFailed", true);
    }.bind(this));
    */

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

  },
  completeTaskUrl: function(adapter) {
  return adapter.buildURL('task', this.content.get('id')) + '/complete'
},
  dismiss: function(){
    $('#token').focus();
    $('#id_alert_wrongtoken > button').click();
    this.set('loginFailed', false);
  }
}

});

export default window.App.LoginController;
