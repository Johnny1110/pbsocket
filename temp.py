from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import base64
import requests

app_id = "f0a670ad9366486d9d9297caa13d017e"
app_key = "sfbKnsJPpqeYLcF3OMI_ip2a1is"


class Auth:
    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(
            self.app_key.encode("utf8"),
            ("x-date: " + xdate).encode("utf8"),
            sha1,
        )
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = (
            'hmac username="'
            + self.app_id
            + '", '
            + 'algorithm="hmac-sha1", '
            + 'headers="x-date", '
            + 'signature="'
            + signature
            + '"'
        )
        return {
            "Authorization": authorization,
            "x-date": format_date_time(mktime(datetime.now().timetuple())),
            "Accept - Encoding": "gzip",
        }
def ubike_station(station):
    auth = Auth(app_id, app_key)
    url = "https://ptx.transportdata.tw/MOTC/v2/Bike/Availability/Taipei?%24format=JSON"
    resp = requests.get(url=url, headers=auth.get_auth_header())
    resp.encoding = "utf-8"
    data = resp.json()

    stationNamesUrl = (
        "https://ptx.transportdata.tw/MOTC/v2/Bike/Station/Taipei?$format=JSON"
    )
    nameDataresp = requests.get(
        url=stationNamesUrl, headers=auth.get_auth_header()
    )
    nameData = nameDataresp.json()

    resultStr = ""

    for info in nameData:
        if station in info['StationName']['Zh_tw']:
            resultStr = info['StationUID']
            break


    mo = requests.get(url, headers=auth.get_auth_header()).json()

    result = {}

    for info in mo:
        if info['StationUID'].__eq__(resultStr):
            result = info
            break
            
    return result


if __name__ == '__main__':
   a = ubike_station("捷運市政府站")
   print(a)