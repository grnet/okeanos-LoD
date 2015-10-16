import Ember from "ember";

export default Ember.Handlebars.makeBoundHelper(function(operand1, operator, operand2) {
  var result;
  switch (operator) {
    case '+':
      result = operand1 + operand2;
      break;
    case '-':
      result = operand1 - operand2;
      break;
    case '*':
      result = operand1 * operand2;
      break;
    case '/':
      result = operand1 / operand2;
      break;
  }
  return result;
});
