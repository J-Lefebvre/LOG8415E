import boto3
import constant
import time


class EC2Creator:
    def __init__(self):
        self.client = boto3.client(
            'ec2',
            region_name="us-east-1",
            aws_access_key_id="ASIAYZCTG2ALWHUZFK54",
            aws_secret_access_key="C2RNAzD4FKUNNzYXYlCspmAbkTLZ1uiAychd5JcZ",
            aws_session_token="FwoGZXIvYXdzEMP//////////wEaDP3leF14mDovpTXIxCLDAX52lezY4yeLYR/xp5mizNRQsw3jt1V0B/nLv73RgxFonmNYzPCGZQ5q2kbYztCiwabHJQY00GY9nZtqh3122HbodrE5gJJ/OHF6x2xboALFN5eNH1J0ZvmnaoIxkmNX9IeTRh7egr3E6OMcYod+Gs1l5+K+RWk511x/8X3zXivBGiFzZottb0cPf1eE/VSPNraf0t8NhBAfxYnYm1zfaIH/uAAWYOLUUzB9CDMwDe55K8Ic/L7F9hlKIuMYRYPVfiJQXii+15aaBjIt+EPWYeqsHbEBsImv+GgQObeq57U+LhCDqF7JM3ki3TWJmpzNDFRZO1MXpIiB"
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
        time.sleep(5)
        return response["Instances"][0]["InstanceId"]

    def create_cluster_t2_large(self):
        self.cluster_t2_instances_ids = [
            self.create_instance(constant.US_EAST_1A, constant.T2_LARGE),
            self.create_instance(constant.US_EAST_1B, constant.T2_LARGE),
            self.create_instance(constant.US_EAST_1C, constant.T2_LARGE),
            self.create_instance(constant.US_EAST_1D, constant.T2_LARGE)
        ]

    def create_cluster_m4_large(self):
        self.cluster_m4_instances_ids = [
            self.create_instance(constant.US_EAST_1A, constant.M4_LARGE),
            self.create_instance(constant.US_EAST_1B, constant.M4_LARGE),
            self.create_instance(constant.US_EAST_1C, constant.M4_LARGE),
            self.create_instance(constant.US_EAST_1D, constant.M4_LARGE)
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