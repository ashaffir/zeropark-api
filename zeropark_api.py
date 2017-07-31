#!/usr/bin/env python3
"""
Conneciton to ZeroPark API
Documentation at:
https://panel.zeropark.com/secure/apidocs/index.html
https://panel.zeropark.com/secure/apidocs/apiguide.pdf
"""
import requests
import json
from datetime import datetime
import pymysql
import time
import logging
import sys
from db_mysql import *

base_url = 'https://panel.zeropark.com/api/'

zp_api_token = 'AAABXU9pW0WfSZA+OLXcWPRZOFml+OnER72riUe9GjRsmNP+vJOFUdD4w0iMNFFD4ribrYM3PeaSEr4rfWGGeA=='

# campaign = "5b0e8340-6728-11e7-afa1-0eda985eb958"
LIMIT = "100"
SORT_COLUMN = ["SPENT", "NAME", "GEO", "TYPE", "BUDGET",
               "STATE", "REDIRECTS", "CONVERSIONS", "PAYOUT"]

HEADER = {'api-token': zp_api_token,
          "access-control-allow-methods": "GET, POST, PUT, DELETE, OPTIONS"}

INTERVAL = ["1=TODAY", "2=YESTERDAY",
            "3=LAST_7_DAYS", "4=THIS_MONTH", "5=LAST_30_DAYS"]


def interval_parser(option):
    if option == 1:
        return 'TODAY'
    elif option == 2:
        return 'YESTERDAY'
    elif option == 3:
        return 'LAST_7_DAYS'
    elif option == 4:
        return 'THIS_MONTH'
    elif option == 5:
        return 'LAST_30_DAYS'
    elif option == 6:
        return 'LAST_MONTH'
    elif option == 7:
        return 'THIS_YEAR'
    elif option == 8:
        return 'LAST_YEAR'
    else:
        return False


def get_campaigns(interval, info):
    api_command = "stats/campaign/all?interval=" + interval + \
        "&page=0&limit=100&sortColumn=SPENT&sortOrder=DESC&showDeleted=false"

    response = requests.get(base_url + api_command, headers=HEADER)
    if response.status_code == 200:
        text_data = response.text
        json_data = json.loads(text_data)
        elements = json_data['elements']
    else:
        print("FAIL to read API data!! Returned status code = {}".format(response.status_code))

    campaign_id_list = []
    campaign_name_list = []

    for i in range(0, len(elements)):
        state = str(elements[i]["details"]["state"]["state"])
        if info == 1 and state == 'ACTIVE':
            campaign_id_list.append(elements[i]["details"]["id"])
            campaign_name_list.append(elements[i]["details"]["name"])
        elif info == 0:
            campaign_id_list.append(elements[i]["details"]["id"])
            campaign_name_list.append(elements[i]["details"]["name"])

    return campaign_name_list, campaign_id_list


def read_campaign_data(campaign_id, required_info, intval):
    api_command = "stats/campaign/" + campaign_id + "/" + required_info + "?interval=" + intval
    response = requests.get(base_url + api_command, headers=HEADER)
    if response.status_code == 200:
        text_data = response.text
        json_data = json.loads(text_data)
        elements = json_data['elements']
    else:
        print("FAIL to read API data!! Returned status code = {}".format(response.status_code))

    return elements


def get_campaign_bid(campaign_id):
    api_command = "stats/campaign/" + campaign_id + "/bid"
    response = requests.get(base_url + api_command, headers=HEADER)
    if response.status_code == 200:
        text_data = response.text
        json_data = json.loads(text_data)
        bid = float(json_data['value'])
    else:
        print("FAIL to read API data!! Returned status code = {}".format(response.status_code))

    return bid


def post_campaign_actions(campaign_id, action, action_value, intval):
    if action == "bid":
        api_command = "campaign/" + campaign_id + "/" + action + "?" + action + "=" + action_value
    elif required_info == "pause":
        api_command = "campaign/" + campaign_id + "/" + action
    elif required_info == "resume":
        api_command = "campaign/" + campaign_id + "/" + action
    else:
        print("Command {} not found. Exiting!!!".format(action))
        sys.exit()

    response = requests.post(base_url + api_command, headers=HEADER)

    if response.status_code != 200:
        print("FAIL to read API data!! Returned status code = {}".format(response.status_code))


def post_source_actions(campaign_id, action, action_value, source_name):
    if action == 1:  # Pause
        api_command = "campaign/" + campaign_id + "/source/pause?hash=" + source_name
        response = requests.post(base_url + api_command, headers=HEADER)
        print("Pausing source {}".format(source_name))
    elif action == 2:  # Resume
        api_command = "campaign/" + campaign_id + "/source/resume?hash=" + source_name
        response = requests.post(base_url + api_command, headers=HEADER)
        print("Resuming source {}".format(source_name))
    elif action == 3:  # Change bid
        api_command = "campaign/" + campaign_id + "/source/bid?" + \
            "hash=" + source_name + "&bid=" + action_value
        response = requests.post(base_url + api_command, headers=HEADER)
        print("Changing source {} to bid {}".format(source_name, action_value))
    else:
        print("Command {} not found. Exiting!!!".format(action))
        sys.exit()

    if response.status_code != 200:
        print("FAIL to read API data!! Returned status code = {}".format(response.status_code))


def post_target_action(campaign_id, action, action_value, target_name):
    if action == 1:  # Pause
        api_command = "campaign/" + campaign_id + "/target/pause?hash=" + target_name
    elif action == 2:  # Resume
        api_command = "campaign/" + campaign_id + "/target/resume?hash=" + target_name
    elif action == 3:  # Change bid
        api_command = "campaign/" + campaign_id + "/target/bid?" + \
            "hash=" + target_name + "&bid=" + action_value
    else:
        print("Command {} not found. Exiting!!!".format(action))
        sys.exit()

    response = requests.post(base_url + api_command, headers=HEADER)

    if response.status_code != 200:
        print("FAIL to read API data!! Returned status code = {}".format(response.status_code))


def display_campaign_data(campaign_id, camp_data, info, interval):
    counter = 0
    if info == 'targets':
        for target in camp_data:
            if target["stats"]["redirects"] > 0:
                print("Campaign = {}".format(campaign_id))
                print(">>>>>>>> {}) TARGET = {}".format(counter, target["target"]))
                print("redirects = {}".format(target["stats"]["redirects"]))
                print("top_bid = {}".format(target["bidPosition"]["topBid"]))
                print("position = {}".format(target["bidPosition"]["position"]))
                print("state = {}".format(target["state"]["state"]))
                print("#" * 30)
                counter += 1
    elif info == 'sources':
        for source in camp_data:
            if source["stats"]["redirects"] > 0:
                print("Campaign = {}".format(campaign_id))
                print(">>>>>>>> {}) SOURCE = {}".format(counter, source["source"]))
                print("redirects = {}".format(source["stats"]["redirects"]))
                print("spent = {}".format(source["stats"]["spent"]))
                print("payout = {}".format(source["stats"]["payout"]))
                print("average_bid = {}".format(source["stats"]["averageBid"]))
                print("conversions = {}".format(source["stats"]["conversions"]))
                print("state = {}".format(source["state"]["state"]))
                print("#" * 30)
                counter += 1
    else:
        print("ERROR input data - info")
