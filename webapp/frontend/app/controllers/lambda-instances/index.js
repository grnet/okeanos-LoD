import Ember from 'ember';
import pagedArray from 'ember-cli-pagination/computed/paged-array';

export default Ember.ArrayController.extend({
  verify: true,
  confirm: false,
  queryParams: ["page", "perPage"],

  page: 1,
  perPage: 10,
  firstOfCurrentPage: Ember.computed('page', 'perPage', function() {
    if(this.get('model.length') === 0) {
      return 0;
    }
    else {
      return (this.get('page')-1)*(this.get('perPage'))+1;
    }
  }),
  lastOfCurrentPage: Ember.computed('page', 'perPage', 'content', function() {
    return Math.min(this.get('content.length'), (this.get('page'))*(this.get('perPage')));
  }),

  pagedContent: pagedArray('content', {pageBinding: "page", perPageBinding: "perPage"}),

  totalPagesBinding: "pagedContent.totalPages",

  actions: {
    close_alert: function()
    {
      var alert = document.getElementById('alert');
      alert.hidden=true;
    },
    start_stop: function()
    {
      this.set("confirm", false);
      var _this = this;
      Ember.run.later((function () {
        _this.set("request", false);
      }), 4000);
    },
    verify: function(started_app)
    {
      if (started_app)
      {
        var con = window.confirm("There is a deployed application currently running on this lambda-instance.\nIf you want to stop it press ok and then press again the STOP button.");
        if (con)
        {
          this.set("verify", false);
          this.set("confirm", true);
        }
        else{
          this.set("verify", true);
        }
      }
      else {
        this.set("confirm", false);
        var _this = this;
        Ember.run.later((function () {
          _this.set("request", false);
        }), 4000);
      }
    },
  },
});
