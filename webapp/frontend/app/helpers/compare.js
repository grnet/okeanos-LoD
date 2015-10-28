import Ember from "ember";

export default Ember.Helper.helper(function(parameters) {
  var operand1 = parameters[0];
  var operator = parameters[1];
  var operand2 = parameters[2];
  switch (operator) {
    case '<=':
      return operand1 <= operand2;
    case '>=':
      return operand1 >= operand2;
    case '===':
      return operand1 === operand2;
    case '!==':
      return operand1 !== operand2;
    case '==':
      return operand1 == operand2;
  }
});
