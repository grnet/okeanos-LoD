import ApplicationAdapter from './application';

export default ApplicationAdapter.extend({
  host: 'http://localhost:80',
  namespace: 'backend/authenticate',
  headers: {
  'Authorization': App.token
  }
});
