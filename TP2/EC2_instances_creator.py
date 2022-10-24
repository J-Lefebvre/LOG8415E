import boto3
import constant
import time


class EC2Creator:
    def __init__(self):
        self.client = boto3.client('ec2')
        self.open_http_port()
        self.instance_id = None

    # Runs a request to create an instance from parameters and saves their ids
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

    # Main function that creates the instance
    def create_m4_instance(self):
        self.instance_id = self.create_instance(constant.US_EAST_1A, constant.M4_LARGE)
        return self.instance_id

    # Termination function that terminates the running instance
    def terminate_instance(self):
        self.client.terminate_instances(InstanceIds=[self.instance_id])

    # If not done already, opens the port 80 on the default security group so that
    #  the ports of all instances and they are exposed by default on creation
    def open_http_port(self):
        # Gets all open ports on the default group
        opened_ports = [i_protocol.get('FromPort') for i_protocol in
                        self.client.describe_security_groups(GroupNames=[constant.DEFAULT_SECURITY_GROUP_NAME])
                        ['SecurityGroups'][0]['IpPermissions']]
        # if HTTP port not already open, open it
        if constant.HTTP_PORT not in opened_ports:
            self.client.authorize_security_group_ingress(
                GroupName=constant.DEFAULT_SECURITY_GROUP_NAME,
                CidrIp=constant.CIDR_IP,
                FromPort=constant.HTTP_PORT,
                ToPort=constant.HTTP_PORT,
                IpProtocol=constant.IP_PROTOCOL
            )
