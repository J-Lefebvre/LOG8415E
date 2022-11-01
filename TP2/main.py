from EC2_instances_creator import EC2Creator
import constant
import time

ec2 = EC2Creator()

print('Creating instance...')

instance_id = ec2.create_instance(constant.US_EAST_1A, constant.M4_LARGE)
print(f'Instance {instance_id} created!')

print("Waiting 60 seconds before continuing...")
time.sleep(60)

print("""Connect now to the instance to view the results of Hadoop vs Linux vs Spark and \
execute the friendship recommendation algorithm. It may take a few minutes before \
all the results are ready.""")