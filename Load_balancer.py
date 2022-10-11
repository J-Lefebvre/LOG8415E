import boto3
from EC2_instances_creator import EC2Creator
import constant
import time


class LoadBalancer:
    def __init__(self):
        self.elb = boto3.client(
            'elbv2',
            region_name="us-east-1",
            aws_access_key_id="ASIAYZCTG2ALWHUZFK54",
            aws_secret_access_key="C2RNAzD4FKUNNzYXYlCspmAbkTLZ1uiAychd5JcZ",
            aws_session_token="FwoGZXIvYXdzEMP//////////wEaDP3leF14mDovpTXIxCLDAX52lezY4yeLYR/xp5mizNRQsw3jt1V0B/nLv73RgxFonmNYzPCGZQ5q2kbYztCiwabHJQY00GY9nZtqh3122HbodrE5gJJ/OHF6x2xboALFN5eNH1J0ZvmnaoIxkmNX9IeTRh7egr3E6OMcYod+Gs1l5+K+RWk511x/8X3zXivBGiFzZottb0cPf1eE/VSPNraf0t8NhBAfxYnYm1zfaIH/uAAWYOLUUzB9CDMwDe55K8Ic/L7F9hlKIuMYRYPVfiJQXii+15aaBjIt+EPWYeqsHbEBsImv+GgQObeq57U+LhCDqF7JM3ki3TWJmpzNDFRZO1MXpIiB"
        )
        self.load_balancer = None
        self.target_group_t2 = None
        self.target_group_m4 = None

    def create_load_balancer(self):
        self.load_balancer = self.elb.create_load_balancer(
            Type=constant.APPLICATION_LOAD_BALANCER,
            Name='DefaultLoadBalancer',
            IpAddressType=constant.DEFAULT_IP_TYPE,
            Subnets=[
                constant.US_EAST_1A_SUBNET,
                constant.US_EAST_1B_SUBNET,
                constant.US_EAST_1C_SUBNET,
                constant.US_EAST_1D_SUBNET,
            ],
            SecurityGroups=[
                constant.DEFAULT_SECURITY_GROUP_ID,
            ],
        )
        print(self.load_balancer.get('LoadBalancers')[0].get('DNSName'))

    def create_target_group(self, target_type, name, protocol, port, vpc, protocol_version):
        return self.elb.create_target_group(
            TargetType=target_type,
            Name=name,
            Protocol=protocol,
            Port=port,
            VpcId=vpc,
            ProtocolVersion=protocol_version
        )

    def create_target_groups(self):
        self.target_group_t2 = self.create_target_group(
            target_type=constant.TG_TARGET_TYPE,
            name=constant.TG_NAME_T2,
            protocol=constant.TG_PROTOCOL,
            port=constant.DEFAULT_PORT,
            vpc=constant.TG_VPC,
            protocol_version=constant.TG_PROTOCOL_VERSION,
        )

        self.target_group_m4 = self.create_target_group(
            target_type=constant.TG_TARGET_TYPE,
            name=constant.TG_NAME_M4,
            protocol=constant.TG_PROTOCOL,
            port=constant.DEFAULT_PORT,
            vpc=constant.TG_VPC,
            protocol_version=constant.TG_PROTOCOL_VERSION,
        )

    def register_cluster(self, target_group, cluster_ids):
        self.elb.register_targets(
            TargetGroupArn=target_group.get('TargetGroups')[0].get('TargetGroupArn'),
            # All the instances
            Targets=
            [
                {
                    'Id': cluster_id,
                    'Port': constant.DEFAULT_PORT
                }
                for cluster_id in cluster_ids
            ]
        )


ec2 = EC2Creator()
LB = LoadBalancer()

print('Creating clusters...')
t2_cluster, m4_cluster = ec2.create_clusters()
print('Clusters created!')

time.sleep(30)

print('Creating target groups...')
# create target groups
LB.create_target_groups()
print('Target groups created!')

print('Registering targets...')
# register targets
LB.register_cluster(LB.target_group_t2, t2_cluster)
LB.register_cluster(LB.target_group_m4, m4_cluster)
print('target registration complete!')