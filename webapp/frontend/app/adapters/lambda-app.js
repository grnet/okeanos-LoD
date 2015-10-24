import LoDAdapter from 'frontend/adapters/application';

export default LoDAdapter.extend({
  pathForType: function () {
    return 'apps';
  },
  shouldBackgroundReloadRecord: function(){
    return true;
  }
});
