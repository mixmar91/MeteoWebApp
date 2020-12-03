import slack
from flask import Flask
from slackeventsapi import SlackEventAdapter
import slackAPI as slackAPI
import meteo
import json

# read config json file
with open('meteoConfig.json') as f:
  configJson = json.load(f)

app = Flask(__name__)

slack_event_adapter = SlackEventAdapter(configJson['SLACK_SIGNING_SECRET'], '/slack/events', app)

client = slack.WebClient(token=configJson['MeteoBotToken'])
BOT_ID = client.api_call("auth.test")['user_id']

@ slack_event_adapter.on('message')
def message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text = event.get('text')
    splitted = text.split(' ')
    print([event,channel_id,user_id,text])

    # not a bot user
    if user_id != None and BOT_ID != user_id:
        if channel_id == configJson['MeteoChannelId']:
            try:
                if text == "help":
                    # to-do add help response
                    meteo.helpMe()
                elif text == "show regions":
                    # to-do add help response
                    meteo.showRegions()
                elif len(splitted)==3:
                    if splitted[0] == "meteo":
                        # get the first argument as city id
                        cityId = splitted[1]
                        # get the second argument as number of days to get the forecast
                        daysToScrape = int(splitted[2])

                        # create meteo url
                        url= 'https://www.meteo.gr/cf.cfm?city_id='+cityId

                        # each day have 8 row of data
                        numberOfDataToSend = 8*daysToScrape

                        # meteo have forecast data only for the next 5 days
                        if numberOfDataToSend>43:
                            numberOfDataToSend = 43
                        meteo.sendForecastReport(url,numberOfDataToSend)
                    elif splitted[0] == "show" and splitted[1] == "cities":
                        # get the first argument as city id
                        regionId = int(splitted[2])
                        meteo.showRegionCities(regionId)
                else:
                    slackAPI.sendSlackMessage(configJson['MeteoBotToken'], configJson['MeteoChannel'],"Invalid message, please try again!")
            except:
                slackAPI.sendSlackMessage(configJson['MeteoBotToken'], configJson['MeteoChannel'],"Invalid message, please try again!")

if __name__ == "__main__":
    app.run(debug=True)
