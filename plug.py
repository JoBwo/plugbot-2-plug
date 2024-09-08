import json
import os.path
import time

import requests
import argparse
import yaml

from pbc2 import ping, network, custom_command, nmap

import signal
import sys

def signal_handler(sig, frame):
    print("\nThank you for using PlugBot 2.0. Bye!")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


parser = argparse.ArgumentParser(prog="C2C plug script",
                                 description="This script interact with the C2C server.")

parser.add_argument("-e", "--enroll", action="store_true")
parser.add_argument("-p", "--password", action="store_true")
parser.add_argument("-q", "--query", action="store_true")

args = parser.parse_args()

def start_enrollment():
    # If the plug.yaml file exists, we clear it out during this process

    plug_id = input("What should this plug be called? ")
    url = input("Provide the link for your C&C server, e.g. https://hack.me: ") + "/api"

    with open("plug.yaml", "w+") as f:
        f.write(yaml.dump({"plug_id": plug_id, "url": url}))

    # Here we would ask for the server URL but we are lazy

    # We reqeust to the specified URL to start enrolling this plug.
    # Firstly, we tell the server, that this plug wants to register.

    try:

        answer = requests.post(url + "enroll", json={"plug_id": plug_id}).json()

        # If the code is 200, everything is ok.

        if answer["code"] != 200:
            print("The enrollment could not be started. Reason:\n{}".format(answer["error"]))
            exit(1)

        print("The enrollment process was started. Please check the server for the assigned password.")
        print("Then re-run this script with the following options:")
        print("python3 plug.py -e -p")
    except Exception:
        print("The server could not be contacted. Please check your input data.")
        exit(1)

def verify_password():
    # We try to read the plug.yaml. If it does not exist, we print an error

    if not os.path.exists("plug.yaml"):
        print("The plug.yaml file could not be found. Please start enrollment via 'python3 plug.py -e'.")
        exit(1)

    with open("plug.yaml", "r") as f:
        plug_data = yaml.safe_load(f)

    # We ask the user for the secret, verify, and if all  done save the key

    plug_data["secret"] = input("Please input the secret, the server selected for this plug: ")

    try:

        answer = requests.post(plug_data["url"] + "enroll/secret", json=plug_data).json()

        if answer["code"] != 200:
            print("The enrollment could not be started. Reason:\n{}".format(answer["error"]))
            exit(1)

        # We reach here, the plug is enrolled. We save the data
        with open("plug.yaml", "w+") as f:
            f.write(yaml.dump(plug_data))

        print("Your plug is enrolled. You can now scan for new jobs via 'python3 plug.py -q'")
        exit(0)

    except Exception:
        print("The server could not be contacted. Please check your input data.")
        exit(1)


def query_jobs(server_url: str, plug_id: str, secret: str):
    answer = requests.post(server_url + "jobs/get", json={"plug_id": plug_id,
                                                           "secret": secret})
    if len(answer.json()) == 0:
        print("No jobs to query.")

    for job in answer.json():
        result = None
        print("Executing module '{}' with KwArgs '{}'".format(job["module"], json.dumps(job["kwargs"])))
        if job["module"] == "ping":
            # Execute ping
            result = ping.ping(**job["kwargs"])
        elif job["module"] == "ipcheck":
            result = network.ipcheck(**job["kwargs"])
        elif job["module"] == "command":
            result = custom_command.custom_command(**job["kwargs"])
        elif job["module"] == "nmap-sn":
            result = nmap.nmap_sn(**job["kwargs"])

        # We send the result to the server
        requests.post(server_url + "jobs/update", json={"plug_id": plug_id,
                                                              "secret": secret,
                                                              "job_id": job["job_id"],
                                                              "result": result})

def verify_enrollment():
    # This does a simple request to check whether the plug is enrolled into the system.
    if not os.path.exists("plug.yaml"):
        print("The plug.yaml file could not be found. Please start enrollment via 'python3 plug.py -e'.")
        exit(1)

    with open("plug.yaml", "r") as f:
        plug_data = yaml.safe_load(f)

    if not "url" in plug_data or not "plug_id" in plug_data or not "secret" in plug_data:
        print("File 'plug.yaml' missing attributes. Please re-enroll the plug.")
        exit(1)

    answer = requests.post(plug_data["url"] + "plug/verify", json={"plug_id": plug_data["plug_id"],
                                                                "secret": plug_data["secret"]})

    if answer.json()["code"] == 200:
        return plug_data["url"], plug_data["plug_id"], plug_data["secret"]

    print("Could not verify the PlugBot with the backend. Please re-enroll the PlugBot.")
    exit(1)

def do_loop(server_url: str, plug_id: str, secret: str):
    while True:
        starttime = time.time()
        print("Starting loop at {}".format(starttime))

        # Query the jobs
        query_jobs(server_url, plug_id, secret)

        # Calculate the time, it took the fobs to execute
        execution_time = time.time() - starttime
        print("Execution for all current jobs took {} seconds".format(int(execution_time)))

        # Set execution_time to 0, if negative
        execution_time = 60 if execution_time > 60 else execution_time
        wait_time = 60 - execution_time
        print("...Waiting for {} seconds".format(int(wait_time)))

        time.sleep(60.0 - execution_time)



if __name__ == "__main__":
    # We try to find out, what the user wants to do
    if args.enroll and args.password:
        # We want to do enrollment step 2
        verify_password()
    elif args.enroll:
        # We want to do enrollment step 1
        start_enrollment()
    elif args.query:
        # We query all current not dispatched jobs from the server and execute them
        server_url, plug_id, secret = verify_enrollment()
        query_jobs(server_url, plug_id, secret)
    else:
        # We do the default loop
        server_url, plug_id, secret = verify_enrollment()
        do_loop(server_url, plug_id, secret)

