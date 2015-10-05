import DS from "ember-data";

App.ApplicationAdapter = DS.Adapter.extend({
  host: 'http://localhost:80'
});

export default App.ApplicationAdapter;
