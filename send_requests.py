import constant
import requests
import time
import threading


def send_GET_request(cluster_route):
    elb_dns = open(constant.LB_ADDRESS_PATH).readline()
    url = f'http://{elb_dns}/{cluster_route}'
    response = requests.get(url)


def run_test_scenario_1():
    print("Thread 1 start")
    for _ in range(1000):
        send_GET_request(cluster_route='cluster1')
        send_GET_request(cluster_route='cluster2')

    print("Thread 1 end")   


def run_test_scenario_2():
    print("Thread 2 start")
    for _ in range(500):
        send_GET_request(cluster_route='cluster1')
        send_GET_request(cluster_route='cluster2')

    time.sleep(60)

    for _ in range(1000):
        send_GET_request(cluster_route='cluster1')
        send_GET_request(cluster_route='cluster2')

    print("Thread 2 end")


if __name__ == "__main__":

    thread_1 = threading.Thread(target=run_test_scenario_1)
    thread_2 = threading.Thread(target=run_test_scenario_2)

    # Start threads
    thread_1.start()
    thread_2.start()

    # Wait for threads to terminate
    thread_1.join()
    thread_2.join()