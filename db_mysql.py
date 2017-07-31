#! /usr/bin/env python3
"""
MySQL connection module
"""
import pymysql
import time
import datetime
# import csv

DB_NAME = 'zeropark_db'

"""
SQL Commands for the tables:
############################

CREATE TABLE targets(
time_frame VARCHAR(30),
campaign_id VARCHAR(100) NOT NULL,
entry_time DATETIME NOT NULL,
target_name VARCHAR(100) NOT NULL PRIMARY KEY,
spent FLOAT NOT NULL,
redirects INT NOT NULL,
conversions INT NOT NULL,
average_bid FLOAT NOT NULL,
state ENUM('ACTIVE', 'NA') NOT NULL,
traffic_source_type VARCHAR(50),
top_bid FLOAT,
position INT
);

CREATE TABLE sources(
time_frame VARCHAR(30),
campaign_id VARCHAR(100) NOT NULL,
entry_time DATETIME NOT NULL,
source_name VARCHAR(100) NOT NULL PRIMARY KEY,
spent FLOAT NOT NULL,
redirects INT NOT NULL,
conversions INT NOT NULL,
average_bid FLOAT NOT NULL,
state ENUM('ACTIVE', 'NA') NOT NULL,
traffic_source_type VARCHAR(50) NOT NULL
);
"""


def db_onnection():
    cnx = pymysql.connect(host='localhost',
                          user='root',
                          password='1q@W#E$R5t')
    c = cnx.cursor()

    return c, cnx


def insert_campaign_data(campaign_id, campaign_data, info, interval):
    c, cnx = db_onnection()
    c.execute("USE {};".format(DB_NAME))

    for i in range(0, len(campaign_data)):
        if info == 'targets':
            if campaign_data[i]["stats"]["redirects"] > 0:
                try:
                    c.execute("INSERT INTO targets ( \
                            campaign_id, \
                            time_frame, \
                            entry_time, \
                            target_name, \
                            spent, \
                            redirects, \
                            conversions, \
                            average_bid, \
                            state, \
                            traffic_source_type, \
                            top_bid, \
                            position) \
                            values (%s, % s, % s, % s, % s, % s, % s, %s, %s, %s, %s, %s)", (
                        campaign_id,
                        interval,
                        datetime.today(),
                        campaign_data[i]["target"],
                        campaign_data[i]["stats"]["spent"],
                        campaign_data[i]["stats"]["redirects"],
                        campaign_data[i]["stats"]["conversions"],
                        campaign_data[i]["stats"]["averageBid"],
                        campaign_data[i]["state"]["state"],
                        campaign_data[i]["trafficSourceType"],
                        campaign_data[i]["bidPosition"]["topBid"],
                        campaign_data[i]["bidPosition"]["position"]
                    )
                    )
                    print("ADDING TARGET {} to the {} database".format(
                        campaign_data[i]["target"], DB_NAME))
                except Exception as ex:
                    print("Failed to write target {} in DB.".format(campaign_data[i]["target"]))
                    print(ex)

        elif info == 'sources':
            if campaign_data[i]["stats"]["redirects"] > 0:
                try:
                    c.execute(
                        "INSERT INTO sources ( \
                                        campaign_id, \
                                        time_frame, \
                                        entry_time, \
                                        source_name, \
                                        spent, \
                                        redirects, \
                                        conversions, \
                                        average_bid, \
                                        state, \
                                        traffic_source_type) \
                                        values (%s, % s, % s, % s, % s, % s, % s, %s, %s, %s)", (
                            campaign_id,
                            interval,
                            datetime.today(),
                            campaign_data[i]["source"],
                            campaign_data[i]["stats"]["spent"],
                            campaign_data[i]["stats"]["redirects"],
                            campaign_data[i]["stats"]["conversions"],
                            campaign_data[i]["stats"]["averageBid"],
                            campaign_data[i]["state"]["state"],
                            campaign_data[i]["trafficSourceType"],
                        )
                    )
                    print("ADDING SOURCE {} to the {} database".format(
                        campaign_data[i]["source"], DB_NAME))
                except Exception as ex:
                    print("Failed to write source {} in DB.".format(campaign_data[i]["source"]))
                    print(ex)
        else:
            print("NOT SUPPORTED YET!!")
            sys.exit()

    cnx.commit()
    c.close()
    cnx.close()
