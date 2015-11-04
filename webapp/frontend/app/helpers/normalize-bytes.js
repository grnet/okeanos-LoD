import Ember from "ember";

export default Ember.Helper.helper(function(value) {
  if (value < 1024) {
    return value.toString().concat("Bytes");
  }
  else if (value < 1024 * 1024) {
    value = Math.floor(value / 1024);
    return value.toString().concat("KB");
  }
  else if (value < 1024 * 1024 * 1024) {
    value = Math.floor(value / (1024 * 1024));
    return value.toString().concat("MB");
  }
  else {
    value = Math.floor(value / (1024 * 1024 * 1024));
    return value.toString().concat("GB");
  }
});
