import constant
import requests
import time
import threading


def send_GET_request(url):
    response = requests.get(url)


def run_test_scenario_1(url_cluster_1, url_cluster_2):
    print("Thread 1 start")

    for _ in range(1000):
        send_GET_request(url_cluster_1)
        send_GET_request(url_cluster_2)

    print("Thread 1 end")   


def run_test_scenario_2(url_cluster_1, url_cluster_2):
    print("Thread 2 start")
    for _ in range(500):
        send_GET_request(url_cluster_1)
        send_GET_request(url_cluster_2)

    time.sleep(60)

    for _ in range(1000):
        send_GET_request(url_cluster_1)
        send_GET_request(url_cluster_2)

    print("Thread 2 end")


if __name__ == "__main__":


    # Fetch ELB dns address
    elb_dns = open(constant.LB_ADDRESS_PATH).readline()
    url_cluster_1 = f'http://{elb_dns}/cluster1'
    url_cluster_2 = f'http://{elb_dns}/cluster2'

    thread_1 = threading.Thread(target=run_test_scenario_1, args=(url_cluster_1,url_cluster_2))
    thread_2 = threading.Thread(target=run_test_scenario_2, args=(url_cluster_1, url_cluster_2))

    # Start threads
    thread_1.start()
    thread_2.start()

    # Wait for threads to terminate
    thread_1.join()
    thread_2.join()