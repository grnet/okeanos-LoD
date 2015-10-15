import Ember from "ember";
import GenericAdapter from 'frontend/adapters/application';

export default GenericAdapter.extend({
  shouldReloadAll: function(){
    return true;
  },
});