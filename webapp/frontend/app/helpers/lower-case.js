import Ember from "ember";

export default Ember.Helper.helper(function([str]) {
  return str.toLowerCase();
});
