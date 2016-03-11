import Ember from "ember";

export default Ember.Helper.helper(function([currentPath, mode]) {
	var pathRoot = currentPath.split(".")[0];

	if(pathRoot === mode){
		return "active treeview";
	}

	return "";
});
