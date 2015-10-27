import GenericAdapter from 'frontend/adapters/application';

export default GenericAdapter.extend({
  pathForType: function() {
    return 'apps/count';
  }
});
