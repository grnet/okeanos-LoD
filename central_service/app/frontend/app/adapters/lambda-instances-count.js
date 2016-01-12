import GenericAdapter from 'frontend/adapters/application';

export default GenericAdapter.extend({
  pathForType: function() {
    return 'lambda_instances/count';
  }
});
