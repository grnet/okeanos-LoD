import ApplicationAdapter from './application';
import config from '../config/environment';

export default ApplicationAdapter.extend({
  host: config.host + ':80',
  namespace: 'api/lambda-instances/'
});
