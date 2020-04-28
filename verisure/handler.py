import requests
import datetime
from cognite.client.data_classes import Asset
from cognite.client.data_classes import TimeSeries
from cognite.client import CogniteClient

import os

import verisure

username = secrets.USERNAME
password = secrets.PASSWORD
apikey = secrets.COGNITE_API_KEY


# Live update Alarm and Lock
def f(x):
    return {
        'DISARMED': 0,
        'ARMED': 1,
    }[x]


def g(x):
    return {
        'UNLOCKED': 0,
        'LOCKED': 1,
    }[x]


def stream_verisure_data():
    # endpoints = [["_Alarm_","armState"], ["_Door_", "doorLockStatusList"], ["_Climate_", "climateValues"]]
    # print ("Started while loop at " + str(time.gmtime()))
    # while True:

    # Alarm
    while True:
        for house in session.installations:
            try:
                giid = house['giid']
                owner = ''

                if giid == '7878017037':
                    owner='MG_'
                session.set_giid(giid)
                data_response = session.get_overview()
            except:
                print("Failed to get data from Verisure, response code: ")
                time.sleep(1)
            Climate_data = data_response['climateValues']
            Alarm_data = data_response['armState']
            Locked_data = data_response['doorLockStatusList'][0]
            date_alarm = Alarm_data['date']
            date_locked = Locked_data['eventTime']
            datetime_object_alarm = datetime.strptime(date_alarm.replace("T", "-").replace(".000Z", "").replace(":", "-"),
                                                      '%Y-%m-%d-%H-%M-%S')
            datetime_object_locked = datetime.strptime(date_locked.replace("T", "-").replace(".000Z", "").replace(":", "-"),
                                               '%Y-%m-%d-%H-%M-%S')

            # for statusTy      pe, date in Alarm_data.items():
            try:
                timeseries.post_datapoints(owner+"Alarm_bool", [dto.Datapoint(datetime_object_alarm, f(Alarm_data['statusType']))])
                timeseries.post_datapoints(owner+"Alarm", [dto.Datapoint(datetime_object_alarm, Alarm_data['statusType'])])
                timeseries.post_datapoints(owner+"Lock_bool",
                                           [dto.Datapoint(datetime_object_locked, g(Locked_data['currentLockState']))])
                timeseries.post_datapoints(owner+"Lock", [dto.Datapoint(datetime_object_locked, Locked_data['currentLockState'])])
                for sensor in Climate_data:
                    temperature = sensor['temperature']
                    name = sensor['deviceLabel'].replace(" ", "-")
                    try:
                        humidity = sensor['humidity']
                    except:
                        print("No humidity")
                    date = sensor['time']
                    datetime_object = datetime.strptime(date.replace("T", "-").replace(".000Z", "").replace(":", "-"),
                                                        '%Y-%m-%d-%H-%M-%S')
                    try:
                        timeseries.post_datapoints(name + "-temp", [dto.Datapoint(datetime_object, temperature)])
                        try:
                            timeseries.post_datapoints(name + "-humidity", [dto.Datapoint(datetime_object, humidity)])
                        except:
                            print("No humidity")
                    except:
                        print("Failed to insert datapoint in CDP")
                        print(name)
            except:
                print("Failed to insert datapoint in CDP")
            time.sleep(1)


if __name__ == "__main__":
    session = verisure.Session(username, password)
    session.login()
    session._get_installations()
    project = "verisure"
    config.configure_session(api_key=apikey, project=project, cookies=None)
    stream_verisure_data()
