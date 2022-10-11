import boto3
import constant

class EC2Creator:
    def __init__(self):
        self.client = boto3.client(
            'ec2',
            region_name="us-east-1",
            aws_access_key_id="",
            aws_secret_access_key="",
            aws_session_token=""
        )

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
            # default key_pair
            KeyName=constant.DEFAULT_KEY_PAIR,

            # Availability zone
            Placement={
                'AvailabilityZone': availability_zone,
            },

            # Security groups
            SecurityGroups=[
                constant.DEFAULT_SECURITY_GROUP,
            ],
            DisableApiTermination=False,

            # One instance
            MaxCount=1,
            MinCount=1
        )
        print(response["Instances"][0]["InstanceId"])
        return response["Instances"][0]["InstanceId"]

    def create_cluster_t2_large(self):
        self.cluster_t2_instances_ids = [
            self.create_instance(constant.US_EAST_1A, constant.T2_LARGE),
            self.create_instance(constant.US_EAST_1B, constant.T2_LARGE),
            self.create_instance(constant.US_EAST_1C, constant.T2_LARGE),
            self.create_instance(constant.US_EAST_1D, constant.T2_LARGE),
            self.create_instance(constant.US_EAST_1E, constant.T2_LARGE)
        ]

    def create_cluster_m4_large(self):
        self.cluster_m4_instances_ids = [
            self.create_instance(constant.US_EAST_1A, constant.M4_LARGE),
            self.create_instance(constant.US_EAST_1B, constant.M4_LARGE),
            self.create_instance(constant.US_EAST_1C, constant.M4_LARGE),
            self.create_instance(constant.US_EAST_1D, constant.M4_LARGE),
            self.create_instance(constant.US_EAST_1E, constant.M4_LARGE)
        ]

    def create_clusters(self):
        self.create_cluster_t2_large()
        self.create_cluster_m4_large()


obj = EC2Creator()
obj.create_clusters()

print(obj.cluster_t2_instances_ids)
print(obj.cluster_m4_instances_ids)
