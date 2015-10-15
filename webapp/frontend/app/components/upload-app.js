import Ember from 'ember';

export default Ember.Component.extend({
  actions : {
    upload: function(app) {
      app.set('description', this.get("description"));
      app.set('project_name', this.get("project_name"));
      app.set('file', this.$("input[name='file']")[0].value);
      app.set('type', this.$("select[name='type']")[0].value);

      app.save();
    }
  }

});
