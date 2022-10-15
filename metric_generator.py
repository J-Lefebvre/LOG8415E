from datetime import datetime, timedelta
import boto3
import pandas as pd
import matplotlib.pyplot as plt

# TODO: Adjust Startimes and periods to retrieve acceptable metric results.

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
        #list of chosen metrics 
        self.metrics_target_group = ['UnHealthyHostCount', 'HealthyHostCount', 'TargetResponseTime', 'RequestCount', 'HTTPCode_Target_4XX_Count', 'HTTPCode_Target_2XX_Count', 'RequestCountPerTarget']
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
                StartTime=datetime.utcnow() - timedelta(minutes=10),
                EndTime=datetime.utcnow(),
                Period=60,
                Statistics=['Minimum', 'Maximum', 'Average']
            )

        return statistics


    def build_target_group_metric_queries(self, cluster_id, cluster_type):
        """Build the queries to specify which target group metric data to retrieve. """

        metric_queries = []
        for metric in self.metrics_target_group:
            metric_queries.append({
                    'Id': metric.lower() + 'TargetGroup' + cluster_type,
                    'MetricStat': {
                        'Metric': {
                            'Namespace': 'AWS/ApplicationELB',
                            'MetricName': metric,
                            "Dimensions": [
                            {
                                'Name': 'TargetGroup',
                                'Value': cluster_id
                            },
                            {
                                'Name': 'LoadBalancer',
                                'Value': self.elb_id
                            }
                            ],
                        },
                        'Period': 60*60, # Change this 
                        'Stat': 'Sum',
                    }
                })
            
        return metric_queries


    # To get metrics from clusters
    def get_target_group_metric_data(self, cluster_id, cluster_type):
        """Retrieve datapoints for each chosen metric. """

        metric_query = self.build_target_group_metric_queries(cluster_id, cluster_type)

        response = self.cloudwatch.get_metric_data(
            MetricDataQueries=metric_query,
            StartTime=datetime.utcnow() - timedelta(days=1),
            EndTime=datetime.utcnow()
        )

        data_cluster = response["MetricDataResults"]

        return data_cluster


    def generate_plots(self, data_cluster_t2, data_cluster_m4):
        """Create and export a plot for each metric using its datapoints."""

        plt.rcParams["figure.figsize"] = 12,5
        for i in range(len(data_cluster_t2)):

            data1_dict = data_cluster_t2[i]
            data2_dict = data_cluster_m4[i] 
            
            # retrieving the metrics label
            metrics_label = data1_dict.get('Label')

            # Convert dictionnary data into pandas
            df_1 = pd.DataFrame.from_dict(data1_dict)[["Timestamps","Values"]]
            df_1.rename(columns={'Values': 'ClusterT2'}, inplace=True)
            df_2 = pd.DataFrame.from_dict(data2_dict)[["Timestamps","Values"]]

            if len(df_1) == 0:
                print(f"ERROR: No datapoints were found for metric {metrics_label} of cluster t2")
            
            if len(df_2) == 0:
                print(f"ERROR: No datapoints were found for metric {metrics_label} of cluster m4")

            # Rename columns
            df_2.rename(columns={'Values': 'ClusterM4'}, inplace=True)

            # Parse strings to datetime type
            df_1["Timestamps"] = pd.to_datetime(df_1["Timestamps"], infer_datetime_format=True)
            df_2["Timestamps"] = pd.to_datetime(df_2["Timestamps"], infer_datetime_format=True)

            
            # Create plot
            if len(df_1)!=0 and len(df_2)!=0:

                print("drawing plot...")
                plt.xlabel("Timestamps")
                plt.plot("Timestamps", "ClusterT2", color="red", data=df_1)
                plt.plot("Timestamps", "ClusterM4", color="blue", data=df_2)
                plt.title(metrics_label)
                handles, labels = plt.gca().get_legend_handles_labels()
                by_label = dict(zip(labels, handles))
                plt.legend(by_label.values(), by_label.keys())
                plt.savefig(f"plots/{metrics_label}")      
            

    def prepare_results(self):
        """Retrieve metrics and report the performance by generating plots and showing statistics."""


        print("retrieving metrics...")
        # Retrieve datapoints of each chosen metric collected from cluster t2
        data_cluster_t2 = self.get_target_group_metric_data(self.cluster_t2_id, 't2')

        # Retrieve datapoints of each chosen metric collected from cluster m4
        data_cluster_m4 = self.get_target_group_metric_data(self.cluster_m4_id, 'm4')


        for i in range(len(data_cluster_t2)):
            print(data_cluster_t2[i])

        # Generate plots for clusters comparison
        #self.generate_plots(data_cluster_t2, data_cluster_m4)

        # # Retrieve statistics of each chosen metric collected from ec2 instances of cluster t2
        # for instance_id in self.cluster_t2_instances_ids:
        #     statistics = self.get_instances_metric_statistics(instance_id)

        #     print(f"CPU Utilization of instance {instance_id} in cluster t2")
        #     print(f"Minimum: {statistics['Datapoints'][0]['Minimum']}%")
        #     print(f"Maximum: {statistics['Datapoints'][0]['Maximum']}%")
        #     print(f"Average: {statistics['Datapoints'][0]['Average']}%\n")

        
        # # Retrieve statistics of each chosen metric collected from ec2 instances of cluster m4
        # for instance_id in self.cluster_m4_instances_ids:
        #     statistics = self.get_instances_metric_statistics(instance_id)

        #     print(f"CPU Utilization of instance {instance_id} in cluster m4")
        #     print(f"Minimum: {statistics['Datapoints'][0]['Minimum']}%")
        #     print(f"Maximum: {statistics['Datapoints'][0]['Maximum']}%")
        #     print(f"Average: {statistics['Datapoints'][0]['Average']}%\n")


# For testing purposes 
if __name__ == "__main__":

    # Change these 
    elb_id = "loadbalancer/app/DefaultLoadBalancer/bc8ed79f8b2c7123"
    cluster_t2_id = "targetgroup/TargetGroupT2/29193be0de6520ed"
    cluster_m4_id = "targetgroup/TargetGroupM4/4b77f266ca9096e4"
    cluster_t2_instances_ids = ["i-005fc8712ccfa4760", "i-00f053ab864ea395e", "i-0894703fdd5ac22c7", "i-001aa8c0205a9d15a"]
    cluster_m4_instances_ids = ["i-0d22aaea47f5f86ea", "i-043a11ee58a826934", "i-06c46d97e5747a961", "i-0311a508edcf4dd9c"]

    metricGenerator = MetricGenerator(
        elb_id = elb_id,
        cluster_t2_id=cluster_t2_id,
        cluster_m4_id=cluster_m4_id,
        cluster_t2_instances_ids=cluster_t2_instances_ids,
        cluster_m4_instances_ids=cluster_m4_instances_ids
    )

    metricGenerator.prepare_results()