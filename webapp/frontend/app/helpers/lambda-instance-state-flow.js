import Ember from "ember";

export default Ember.Helper.helper(function(parameters) {
  var status_message = parameters[0];
  switch (status_message) {
    case "PENDING":
      return "1/8";
    case "CLUSTER_CREATED":
      return "2/8";
    case "INIT_DONE":
      return "3/8";
    case "COMMONS_INSTALLED":
      return "4/8";
    case "HADOOP_INSTALLED":
      return "5/8";
    case "KAFKA_INSTALLED":
      return "6/8";
    case "FLINK_INSTALLED":
      return "7/8";
    case "FLUME_INSTALLED":
      return "8/8";
  }
  return "";
});
