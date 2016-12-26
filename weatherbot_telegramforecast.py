import requests
import time
import urllib
import googlemaps
import pprint
import datetime



#Setup the api key for the third party services (dark sky and google maps),REPLACE BY YOUR API KEY
api_config={}
api_config["dark_sky"]=""
api_config["google_geoloc"]=""
#Setup the google maps client
gmaps = googlemaps.Client(key=api_config["google_geoloc"])
#Setup the URL to collect the weather forecast
darksky_request="https://api.darksky.net/forecast/"
darksky_request_api=darksky_request+api_config["dark_sky"]+"/"

#Setup the api key for the bots on telegram,REPLACE BY YOUR API KEY
bot_config={}
bot_config["weatherforecast_bot"]=""
URL= "https://api.telegram.org/bot{}/".format(bot_config["weatherforecast_bot"])






#Functions of the tutorials to interact with the telegram API and collect data
def get_url(url):
    response = requests.get(url)
    #content = response.content.decode("utf8")
    # print(content)
    return response


def get_json_from_url(url):
    content = get_url(url)
    return content.json()


def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)




#Function to collect the data for the forecast 
def getdetailsweather(lat,lon):
    darksky_request_api_complete = darksky_request_api + str(lat) + "," + str(lon)+"?units=si"
    print(darksky_request_api_complete)
    response = (requests.get(darksky_request_api_complete).json())
    pprint.pprint(response)
    daily_data=response["daily"]["data"]
    current_date=datetime.datetime.now()
    list_messages=[]
    for i,data in enumerate(daily_data):
        print(data,i)
        date=(current_date+datetime.timedelta(days=i)).strftime("%d-%m-%Y")
        print(date)
        message=date+":"+data["summary"]+"\n"+"Tmin="+str(data["temperatureMin"])+"°C\n"+"Tmax="+str(data["temperatureMax"])+"°C\n"+"Precipitation_probabilty="+str(int(100*data["precipProbability"]))+"%\n"
        print(message)
        list_messages.append(message)
    return list_messages

def getgeoloc(text):
    geocode_result = gmaps.geocode(text)
    latitude_longitude = geocode_result[0]["geometry"]["location"]
    print(latitude_longitude)
    return latitude_longitude

def giveweather(updates):
    for update in updates["result"]:
        print(update)
        text = update["message"]["text"]
        print(text)
        chat = update["message"]["chat"]["id"]
        try:
            lat_lon=getgeoloc(text)
            list_messages=getdetailsweather(lat_lon["lat"],lat_lon["lng"])
            for message in list_messages:
                send_message(message, chat)
                time.sleep(0.1)
        except Exception as weather:
            continue




def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            giveweather(updates)
        time.sleep(0.5)


if __name__ == '__main__':
    print("djm_weatherbot is on")
    main()



