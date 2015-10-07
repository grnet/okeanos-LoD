import DS from "ember-data";

var ApplicationAdapter = DS.Adapter.extend({
  host: 'http://localhost:80'
});

export default ApplicationAdapter;
