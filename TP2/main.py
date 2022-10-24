from EC2_instances_creator import EC2Creator
import time
import os

ec2 = EC2Creator()

print('Creating instance...')
instance_id = ec2.create_m4_instance()
print('Instance created!')

print("Waiting 60 seconds before continuing...")
time.sleep(60)

# Terminate services
ec2.terminate_instances()
