from datetime import datetime, timedelta
import json
import random
import boto3
import pandas as pd
import matplotlib.pyplot as plt
class MetricGenerator:
    """ Metric generator used to retrieve CloudWatch metrics of target groups 
    and generate plots.
    """

    def __init__(self, elb_id, cluster_t2_id, cluster_m4_id, cluster_t2_instances_ids, cluster_m4_instances_ids):
        self.cloudwatch = boto3.client('cloudwatch')
        self.elb_id = elb_id
        self.cluster_t2_id = cluster_t2_id
        self.cluster_m4_id = cluster_m4_id        
        self.cluster_t2_instances_ids = cluster_t2_instances_ids
        self.cluster_m4_instances_ids = cluster_m4_instances_ids

        print(self.elb_id)
        print(self.cluster_t2_id)
        print(self.cluster_m4_id)

        #list of chosen metrics
        # self.metrics = [
        #     {'name': 'UnHealthyHostCount', 'stat': 'Average'},
        #     {'name': 'HealthyHostCount', 'stat': 'Average'},
        #     {'name': 'TargetResponseTime', 'stat': 'Average'},
        #     {'name': 'RequestCount', 'stat': 'Sum'},
        #     {'name': 'HTTPCode_Target_4XX_Count', 'stat': 'Sum'},
        #     {'name': 'HTTPCode_Target_2XX_Count', 'stat': 'Sum'},
        #     {'name': 'RequestCountPerTarget', 'stat': 'Sum'},
        # ]
        # self.metrics_load_balancer = [
        #     {'name': 'TargetResponseTime', 'stat': 'Average'},
        #     {'name': 'RequestCount', 'stat': 'Sum'},
        #     {'name': 'HTTPCode_ELB_5XX_Count', 'stat': 'Sum'},
        #     {'name': 'HTTPCode_ELB_503_Count', 'stat': 'Sum'},
        #     {'name': 'HTTPCode_Target_2XX_Count', 'stat': 'Sum'},
        #     {'name': 'ActiveConnectionCount', 'stat': 'Sum'},
        #     {'name': 'NewConnectionCount', 'stat': 'Sum'},
        #     {'name': 'ProcessedBytes', 'stat': 'Sum'},
        #     {'name': 'ConsumedLCUs', 'stat': 'Sum'}
        # ]
        self.metrics_instances = ['CPUUtilization']


    # To get metrics from instances
    def get_instances_metric_statistics(self, instance_id):
        """Retrieve statistics for each chosen metric. """

        for metric in self.metrics_instances:

            statistics = self.cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName=metric,
                Dimensions= [
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    }
                ],
                StartTime=datetime.utcnow() - timedelta(minutes=60),
                EndTime=datetime.utcnow(),
                Period=60,
                Statistics=['Minimum', 'Maximum', 'Average']
            )

        return statistics


    def build_target_group_metric_queries(self, metric_queries, metrics):
        """Build the queries to specify which target group metric data to retrieve. """
        for id, metric in enumerate(metrics):
            metric_queries.append({
                    'Id': f'metric_{id}',
                    'MetricStat': {
                        'Metric': metric,
                        'Period': 60,
                        'Stat': 'Sum' # TODO: change Stat according to the metric
                    }
                })
            
        return metric_queries


    # To get metrics from clusters
    def get_metric_data(self):
        """Retrieve datapoints for each chosen metric. """
        metrics = [m for m in self.cloudwatch.list_metrics()['Metrics'] if (m['Namespace'] == 'AWS/ApplicationELB') if any(True for dim in m['Dimensions'] if elb_id in dim.values())]
        with open('list_metrics.json', 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=4)

        metric_queries = []
        metric_queries = self.build_target_group_metric_queries(metric_queries, metrics)

        with open('metric_queries.json', 'w', encoding='utf-8') as f:
            json.dump(metric_queries, f, ensure_ascii=False, indent=4)

        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=metric_queries,
            StartTime=datetime.utcnow() - timedelta(minutes=60),
            EndTime=datetime.utcnow()
        )

        with open('reponse.json', 'w', encoding='utf-8') as f:
            json.dump(response, f, ensure_ascii=False, indent=4, default=str)

        data_cluster = response["MetricDataResults"]

        return data_cluster


    def generate_plots(self, data):
        """Create and export a plot for each metric using its datapoints."""

        plt.rcParams["figure.figsize"] = 12,5
        for metric in data:
            # Convert dictionary data into pandas
            df = pd.DataFrame.from_dict(metric)[["Timestamps","Values"]]

            if len(df) == 0:
                print(f"ERROR: No datapoints were found for metric {metric['Id']}")

            # Rename columns
            df.rename(columns={'Values': 'Cluster?'}, inplace=True)

            # Parse strings to datetime type
            df["Timestamps"] = pd.to_datetime(df["Timestamps"], infer_datetime_format=True)
            
            # Create plot
            if len(df)!=0:
                print(f"drawing plot {metric['Id']}")
                plt.xlabel("Timestamps")
                plt.plot("Timestamps", "Cluster?", color="red", data=df)
                plt.title(metric['Label'].split(' ')[-1])
                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                plt.legend(by_label.values(), by_label.keys())
                plt.savefig(f"plots/{metric['Id']}")      
            

    def prepare_results(self):
        """Retrieve metrics and report the performance by generating plots and showing statistics."""

        print("retrieving metrics...")
        # Retrieve datapoints of each chosen metric collected from cluster t2
        data = self.get_metric_data()

        # Generate plots for clusters comparison
        self.generate_plots(data)

        # # Retrieve statistics of each chosen metric collected from ec2 instances of cluster t2
        for instance_id in self.cluster_t2_instances_ids:
            statistics = self.get_instances_metric_statistics(instance_id)

            print(f"CPU Utilization of instance {instance_id} in cluster t2")
            print(f"Minimum: {statistics['Datapoints'][0]['Minimum']}")
            print(f"Maximum: {statistics['Datapoints'][0]['Maximum']}")
            print(f"Average: {statistics['Datapoints'][0]['Average']}\n")

        
        # Retrieve statistics of each chosen metric collected from ec2 instances of cluster m4
        for instance_id in self.cluster_m4_instances_ids:
            statistics = self.get_instances_metric_statistics(instance_id)

            print(f"CPU Utilization of instance {instance_id} in cluster m4")
            print(f"Minimum: {statistics['Datapoints'][0]['Minimum']}")
            print(f"Maximum: {statistics['Datapoints'][0]['Maximum']}")
            print(f"Average: {statistics['Datapoints'][0]['Average']}\n")

# # For testing purposes 
# if __name__ == "__main__":

#     # Change these 
#     elb_id = "app/DefaultLoadBalancer/3ccc6002e974c810"
#     cluster_t2_id = "targetgroup/TargetGroupT2/1a6bc739e878fe9c"
#     cluster_m4_id = "targetgroup/TargetGroupM4/e59beeea9f80d7de"
#     cluster_t2_instances_ids = ["i-0c127ddaae6f87c45", "i-0bab82825ee2a16b1", "i-038ef7e92be866bad", "i-04a6ac98871978b9b"]
#     cluster_m4_instances_ids = ["i-092bf41d4b5b39142", "i-0e810023460d7d567", "i-0c4b961ac7cd12dbf", "i-0a79569e39ea136e1"]

#     metricGenerator = MetricGenerator(
#         elb_id = elb_id,
#         cluster_t2_id=cluster_t2_id,
#         cluster_m4_id=cluster_m4_id,
#         cluster_t2_instances_ids=cluster_t2_instances_ids,
#         cluster_m4_instances_ids=cluster_m4_instances_ids
#     )

#     metricGenerator.prepare_results()