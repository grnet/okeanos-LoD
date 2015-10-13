import DS from 'ember-data';

export default DS.JSONAPISerializer.extend({

  keyForAttribute: function(attr) {
    return Ember.String.underscore(attr);
  },

  extractAttributes: function(modelClass, resourceHash) {
    var attributeKey;
    var attributes = {};
    console.debug(resourceHash);

    modelClass.eachAttribute((key) => {
      attributeKey = this.keyForAttribute(key, 'deserialize');
      if (resourceHash.hasOwnProperty(attributeKey)) {
        attributes[key] = resourceHash[attributeKey];
      }
    });
    console.debug(attributes);
    return attributes;
  },

  _extractType: function(modelClass, resourceHash) {
    console.debug(modelClass.modelName);
    return modelClass.modelName;
  },

  normalizeSingleResponse: function(store, primaryModelClass, payload, id, requestType) {
    return this._normalizeResponse(store, primaryModelClass, payload, id, requestType, false);
  }
});
