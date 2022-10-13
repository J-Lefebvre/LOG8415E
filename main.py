from EC2_instances_creator import EC2Creator
from Load_balancer import LoadBalancer
import time
import os

ec2 = EC2Creator()
LB = LoadBalancer()

print('Creating clusters...')
t2_cluster, m4_cluster = ec2.create_clusters()
print('Clusters created!')

time.sleep(60)

# create load balancer
print('Creating load balancer...')
LB.create_load_balancer()
print("load balancer created!")

# create target groups
print('Creating target groups...')
LB.create_target_groups()
print('Target groups created!')

# register targets
print('Registering Instances to target groups...')
LB.register_cluster(LB.target_group_t2, t2_cluster)
LB.register_cluster(LB.target_group_m4, m4_cluster)
print('Instances registration complete!')

print('Registering target groups to load balancer...')
LB.register_target_groups()
print('Target groups registration complete!')

# Send GET requests to EC2 instances
print("Sending get requests to instances")
os.system("docker build -t tp1/send_requests .")
os.system("docker run tp1/send_requests:latest")
print("Requests sent")