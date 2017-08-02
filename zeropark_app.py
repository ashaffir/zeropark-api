#! /usr/bin/env python3
"""
ZeroPark user commands interface
"""
import sys
import os
from datetime import datetime
import time
from zeropark_api import *

# time.sleep(2)

intro = """###############################################
ZeroPark Command interface                  ##
by: Alfred Shaffir                          ##
###############################################
"""
cmds = """
######################################################

COMMAND LIST
------------

1- List ACTIVE campaigns
2- List ALL campaigns
3- Display active targets for campaign (redirects > 0)
4- Display active sources for campaign (redirects > 0)
5- Target actions
6- Source actions
7- Source Filtering
8- Source Monitoring
0- Quit (or press "Enter")

######################################################
"""


def command_parser():
    print(cmds)
    cmd = input("Enter Choice: ")
    return cmd


def commands_display():
    print(cmds)


def source_filtering(campaign_id, CPA):
    bad_sources = []
    bid = get_campaign_bid(campaign_id)
    camp_data = read_campaign_data(campaign_id, 'sources', 'THIS_MONTH')
    mana = int(CPA / bid)
    print("Bid = {} ".format(bid))
    print("MANA = {} / {} = {} impressions".format(CPA, bid, mana))

    source_cnt = 0
    for source in camp_data:
        source_name = source['source']
        source_redirects = source["stats"]["redirects"]
        source_conversions = source["stats"]["conversions"]
        source_state = source["state"]["state"]

        if source_redirects > 3 * mana and source_state == 'ACTIVE':
            bad_sources.append(source_name)
            print("UNDER-PERFORMING source ## {} ##: \n \
            source_state = {} \n \
            source_redirects = {} \n \
            source_conversions = {} \n".format(
                source['source'], source_state, source_redirects, source_conversions))
            source_cnt += 1

    print("Total filtered sources = {}".format(source_cnt))
    print("Under performing sources: {} \n".format(bad_sources))

    if source_cnt > 0:
        user_action = str(input("Pause sources? [y/n] >> "))
        if user_action == 'y':
            for s in bad_sources:
                post_source_actions(campaign_id=campaign_id, action=1,
                                    action_value=0, source_name=s)
            print("Sources were paused!")
        elif user_action == 'n':
            return

    return


def source_monitoring(campaign_id, CPA):
    try:
        while True:
            bad_sources = []
            bid = get_campaign_bid(campaign_id)
            camp_data = read_campaign_data(campaign_id, 'sources', 'LAST_7_DAYS')
            mana = int(CPA / bid)
            print("Bid = {} ".format(bid))
            print("MANA = {} / {} = {} impressions".format(CPA, bid, mana))
            print("THRESHOLD = 3 x {} = {} impressions".format(mana, 3 * mana))

            source_cnt = 0
            for source in camp_data:
                source_name = source['source']
                source_redirects = source["stats"]["redirects"]
                source_conversions = source["stats"]["conversions"]
                source_state = source["state"]["state"]

                if source_redirects > 0.8 * 3 * mana and source_redirects < 3 * mana:
                    print("Approaching threshold: {} with {} redirects".format(
                        source_name, source_redirects))
                elif source_redirects > 3 * mana and source_state == 'ACTIVE':
                    bad_sources.append(source_name)
                    print("UNDER-PERFORMING source ## {} ##: \n \
                    source_state = {} \n \
                    source_redirects = {} \n \
                    source_conversions = {} \n".format(
                        source['source'], source_state, source_redirects, source_conversions))
                    source_cnt += 1
            print("#" * 20)
            print("Time Stamp: ", datetime.datetime.now())
            print("#" * 20)
            print("Total filtered sources = {}".format(source_cnt))
            print("Under performing sources: {} \n".format(bad_sources))

            if source_cnt > 0:
                for s in bad_sources:
                    post_source_actions(campaign_id=campaign_id, action=1,
                                        action_value=0, source_name=s)
                    print("Sources were paused!")

            time.sleep(120)
    except KeyboardInterrupt:
        print('\n Interrupted!!')


def main():
    print(intro)

    while True:
        try:
            user_command = int(command_parser())
        except:
            print("Exiting")
            break

        # Get list of active campaigns
        if user_command == 1:
            # Getting the interval input for the query
            interval = 'TODAY'
            c_name, c_id = get_campaigns(interval, 1)
            print("#" * 70)
            print("            ACTIVE Campaigns Information")
            print("\n")
            print("Campaign Name            |           Campaign ID")
            print("#" * 70)
            print("\n")
            for i in range(0, len(c_id)):
                print("{}       {}".format(c_name[i], c_id[i]))
            print("\n")

        # Get ACTIVE campaigns information
        elif user_command == 2:
            # Getting the interval input for the query
            while True:
                print("Enter Interval")
                print(INTERVAL)
                interval = int(input("Interval: "))
                if interval_parser(interval) == False:
                    print("Wrong interval entered. Try again")
                else:
                    interval = interval_parser(interval)
                    break

            c_name, c_id = get_campaigns(interval, 0)
            print("#" * 70)
            print("            ALL Campaigns Information")
            print("\n")
            print("Campaign Name            |           Campaign ID")
            print("#" * 70)
            print("\n")
            for i in range(0, len(c_id)):
                print("{}       {}".format(c_name[i], c_id[i]))
            print("\n")

        # Display active targets for campaign (redirects > 0)
        elif user_command == 3:
            campaign_id = str(input("Enter campaign ID: "))
            while True:
                print("Enter Interval")
                print(INTERVAL)
                interval = int(input("Interval: "))
                if interval_parser(interval) == False:
                    print("Wrong interval entered. Try again")
                else:
                    interval = interval_parser(interval)
                    break

            logging.basicConfig(level=logging.DEBUG, filename='run.log')
            camp_data = read_campaign_data(campaign_id, 'targets', interval)
            display_campaign_data(campaign_id, camp_data, 'targets', interval)
            # insert_campaign_data(campaign_id, camp_data, 'targets', interval)
            logging.info('Finished')

        # Display active sources for campaign (redirects > 0)
        elif user_command == 4:
            campaign_id = str(input("Enter campaign ID: "))
            # Getting the interval input for the query
            while True:
                print("Enter Interval")
                print(INTERVAL)
                interval = int(input("Interval: "))
                if interval_parser(interval) is False:
                    print("Wrong interval entered. Try again")
                else:
                    interval = interval_parser(interval)
                    break

            logging.basicConfig(level=logging.DEBUG, filename='run.log')
            camp_data = read_campaign_data(campaign_id, 'sources', interval)
            display_campaign_data(campaign_id, camp_data, 'sources', interval)
            # insert_campaign_data(campaign_id, camp_data, 'sources', interval)
            logging.info('Finished')

        # Target Actions
        elif user_command == 5:
            campaign_id = input("Enter campaign id: ")
            print("Specify action: 1-Pause, 2-Resume, 3-Change bid")
            user_action = int(input(">> "))
            target_name = str(input("Enter target name: "))
            bid = str(input("Enter bid (if applicable or 0 for no bid change): "))

            post_target_action(campaign_id, user_action, bid, target_name)

        # Source Actions
        elif user_command == 6:
            campaign_id = input("Enter campaign id: ")
            print("Specify action: 1-Pause, 2-Resume, 3-Change bid, 4-Check State")
            user_action = int(input(">> "))
            source_name = str(input("Enter source name: "))
            bid = str(input("Enter bid (if applicable or 0 for no bid change): "))

            post_source_action(campaign_id, user_action, bid, source_name)

        # Source Filtering
        elif user_command == 7:
            campaign_id = input("Enter campaign id: ")
            cpa = float(input("Specify CPA/Payout: >> "))
            source_filtering(campaign_id, cpa)

        # Source Monitoring
        elif user_command == 8:
            logging.basicConfig(level=logging.DEBUG, filename='run.log')
            campaign_id = input("Enter campaign id: ")
            cpa = float(input("Specify CPA/Payout: >> "))
            source_monitoring(campaign_id, cpa)
            logging.info('Finished')

        elif user_command == 0:
            print("Exiting program")
            sys.exit()
        else:
            print("#" * 40)
            print("Wrong choice, please try again")
            print("#" * 40)
            print("\n")


if __name__ == '__main__':
    main()
