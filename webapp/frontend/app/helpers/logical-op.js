import Ember from "ember";

export default Ember.Helper.helper(function (params) {
  var i;
  var result = params[1];
  switch (params[0]) {
    case 'or':
      for (i = 2; i < params.length; i++) {
        result = params[i] || result;
      }
      break;
    case 'and':
      for (i = 2; i < params.length; i++) {
        result = params[i] && result;
      }
      break;
  }
  return result;
});
