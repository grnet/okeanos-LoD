import Ember from "ember";

export default Ember.Helper.helper(function([curPath, path]) {
  if (curPath.indexOf(path) === -1) {
    return "";
  }
  else {
    return "active treeview";
  }
});
