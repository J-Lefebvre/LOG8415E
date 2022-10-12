import boto3
import constant
import time


class EC2Creator:
    def __init__(self):
        self.client = boto3.client(
            'ec2',
            region_name="us-east-1",
            aws_access_key_id="ASIAYZCTG2ALRBDSKIDM",
            aws_secret_access_key="tkKjqtiCZ2ISj9RpahpeLBTOIP9m4kNxktV9rpxr",
            aws_session_token="FwoGZXIvYXdzEMv//////////wEaDN4do23+2mlv5nZJjiLDATJO3/vmvRS5mIZ7F3O88CUI8+sxPaI2iqQciUEFzCjnIrts+SHofM5Xh7/dbSvX8Jtf7UHDk7uoYmAG+IKtDxWA6pIRtvTuDK5lxHvycACFNw4m7L5irU1OWcweHs+IvXB5atxbArUYnpsfOU4j0OFiyBddZToJFTArC0GJu8jaaZAVz/QKlg3LTuiJ1W+PfobUPYy3Si2tzP/wftS+7NOldcCb/5s3FfXfPt97nQRSAuBoRSi7IroCZPudgsM5Vcs9Gyjnr5iaBjIttZodnWHrAAn2/2Iv1o6qexB0rko6CeHeUJdWidENNYLE0hQc9w5uJ9Ls4BUq"        )

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