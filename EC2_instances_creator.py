import boto3
import constant
import time


class EC2Creator:
    def __init__(self):
        self.client = boto3.client('ec2')
        self.cluster_t2_instances_ids = []
        self.cluster_m4_instances_ids = []

    def create_instance(self, availability_zone, instance_type):
        response = self.client.run_instances(
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        # deleting the storage on instance termination
                        'DeleteOnTermination': True,

                        # 8gb volume
                        'VolumeSize': 8,

                        # Volume type
                        'VolumeType': 'gp2',
                    },
                },
            ],

            # UBUNTU instance
            ImageId=constant.UBUNTU_IMAGE,

            # UBUNTU instance
            InstanceType=instance_type,

            # Availability zone
            Placement={
                'AvailabilityZone': availability_zone,
            },

            DisableApiTermination=False,

            # One instance
            MaxCount=1,
            MinCount=1,

            # Script to launch on instance startup
            UserData=open('launch_script.sh').read()
        )
        print(response["Instances"][0]["InstanceId"])
        time.sleep(5)
        return response["Instances"][0]["InstanceId"]

    def create_cluster_t2_large(self):
        self.cluster_t2_instances_ids = [
            self.create_instance(constant.US_EAST_1A, 't2.micro'),
            self.create_instance(constant.US_EAST_1B, 't2.micro'),
            self.create_instance(constant.US_EAST_1C, 't2.micro'),
            self.create_instance(constant.US_EAST_1D, 't2.micro')
        ]

    def create_cluster_m4_large(self):
        self.cluster_m4_instances_ids = [
            self.create_instance(constant.US_EAST_1A, 't2.micro'),
            self.create_instance(constant.US_EAST_1B, 't2.micro'),
            self.create_instance(constant.US_EAST_1C, 't2.micro'),
            self.create_instance(constant.US_EAST_1D, 't2.micro')
        ]

    def create_clusters(self):
        self.create_cluster_t2_large()
        time.sleep(20)
        self.create_cluster_m4_large()

        return (
            self.cluster_t2_instances_ids,
            self.cluster_m4_instances_ids
        )

    def terminate_instances(self):
        self.client.terminate_instances(InstanceIds=self.cluster_t2_instances_ids)
        self.client.terminate_instances(InstanceIds=self.cluster_m4_instances_ids)