import ApplicationAdapter from './application';

export default ApplicationAdapter.extend({
  namespace: 'backend/authenticate',
  host: 'http://snf-670397.vm.okeanos.grnet.gr:8000',
  headers: {
  'Authorization': App.token
  }
});
