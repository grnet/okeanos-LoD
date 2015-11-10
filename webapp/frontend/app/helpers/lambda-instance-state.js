import Ember from "ember";

export default Ember.Helper.helper(function(parameters) {
  var status_message = parameters[0];
  switch (status_message) {
    case "STARTED":
      return "STARTED";
    case "DESTROYED":
      return "DESTROYED";
    case "FAILED":
    case "CLUSTER_FAILED":
    case "INIT_FAILED":
    case "COMMONS_FAILED":
    case "HADOOP_FAILED":
    case "KAFKA_FAILED":
    case "FLINK_FAILED":
    case "FLUME_FAILED":
      return "FAILED";
    case "STOPPED":
      return "STOPPED";
    case "PENDING":
    case "CLUSTER_CREATED":
    case "INIT_DONE":
    case "COMMONS_INSTALLED":
    case "HADOOP_INSTALLED":
    case "KAFKA_INSTALLED":
    case "FLINK_INSTALLED":
    case "FLUME_INSTALLED":
      return "BUILDING";
    case "STOPPING":
    case "STARTING":
    case "DESTROYING":
      return status_message;
  }
});
