import DS from "ember-data";

// Information about user
var User = DS.Model.extend({
	token : DS.attr('string'), 			// okeanos token
});

export default User;
