import boto3
from EC2_instances_creator import EC2Creator
import constant
import time


class LoadBalancer:
    def __init__(self):
        self.elb = boto3.client(
            'elbv2',
            region_name="us-east-1",
            aws_access_key_id="ASIAYZCTG2ALRBDSKIDM",
            aws_secret_access_key="tkKjqtiCZ2ISj9RpahpeLBTOIP9m4kNxktV9rpxr",
            aws_session_token="FwoGZXIvYXdzEMv//////////wEaDN4do23+2mlv5nZJjiLDATJO3/vmvRS5mIZ7F3O88CUI8+sxPaI2iqQciUEFzCjnIrts+SHofM5Xh7/dbSvX8Jtf7UHDk7uoYmAG+IKtDxWA6pIRtvTuDK5lxHvycACFNw4m7L5irU1OWcweHs+IvXB5atxbArUYnpsfOU4j0OFiyBddZToJFTArC0GJu8jaaZAVz/QKlg3LTuiJ1W+PfobUPYy3Si2tzP/wftS+7NOldcCb/5s3FfXfPt97nQRSAuBoRSi7IroCZPudgsM5Vcs9Gyjnr5iaBjIttZodnWHrAAn2/2Iv1o6qexB0rko6CeHeUJdWidENNYLE0hQc9w5uJ9Ls4BUq"
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
            protocol_version=constant.TG_PROTOCOL_VERSION
        )

    def register_target_group(self, listener, target_group, route, priority):
        self.elb.create_rule(
            ListenerArn=listener.get('Listeners')[0].get('ListenerArn'),
            Actions=[
                    {
                        'TargetGroupArn': target_group.get('TargetGroups')[0].get('TargetGroupArn'),
                        'Type': 'forward'
                    },
            ],
            Conditions=[
                {
                    'Field': constant.PATH_PATTERN_CONDITION,
                    'Values': [route]
                },
            ],
            Priority=priority
        )

    def register_target_groups(self):
        listener = self.elb.create_listener(
            LoadBalancerArn=self.load_balancer.get('LoadBalancers')[0].get('LoadBalancerArn'),
            Port=constant.DEFAULT_PORT,
            Protocol=constant.DEFAULT_PROTOCOL,
            DefaultActions=[
                {
                    # default route is mandatory. '/' will be redirected to T2.large cluster.
                    'TargetGroupArn': self.target_group_t2.get('TargetGroups')[0].get('TargetGroupArn'),
                    'Type': constant.FORWARD_RULE,
                    'Order': 1
                }
            ]
        )

        # registering our custom routes
        self.register_target_group(listener, target_group=self.target_group_t2, route='/cluster1', priority=1)
        self.register_target_group(listener, target_group=self.target_group_m4, route='/cluster2', priority=2)

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
