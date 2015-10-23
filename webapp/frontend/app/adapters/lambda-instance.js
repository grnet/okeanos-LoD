import DS from "ember-data";
import GenericAdapter from 'frontend/adapters/application';

export default GenericAdapter.extend({
  handleResponse: function(status, headers, payload) {
    if (this.isSuccess(status, headers, payload)) {
      return payload;
    }
    else{
      return new DS.InvalidError(payload.errors);
    }
  }
});
