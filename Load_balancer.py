import boto3
import constant

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



obj = LoadBalancer()

obj.create_load_balancer()