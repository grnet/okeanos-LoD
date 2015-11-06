import Ember from "ember";

export default Ember.Helper.helper(function(parameters) {
  var status_message = parameters[0];
  switch (status_message) {
    case "PENDING":
      return "1/7";
    case "CLUSTER_CREATED":
      return "2/7";
    case "INIT_DONE":
      return "3/7";
    case "COMMONS_INSTALLED":
      return "4/7";
    case "HADOOP_INSTALLED":
      return "5/7";
    case "KAFKA_INSTALLED":
      return "6/7";
    case "FLINK_INSTALLED":
      return "7/7";
  }
  return "";
});
