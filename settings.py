#!/usr/bin/python

# weatherbit.io API key for local weather information
currentWeatherAPIURL = 'https://api.weatherbit.io/v2.0/current'
dailyWeatherAPIURL = 'https://api.weatherbit.io/v2.0/forecast/daily'
minutelyWeatherAPIURL = 'https://api.weatherbit.io/v2.0/forecast/minutely'
weatherAPIKey = 'ENTER KEY HERE'

# search google to get the Latitude/Longitude for your home location
latitude = <Lat in degrees>
longitude = <Long in degrees>
locationName = "Name of location" 

# set number of days to forecast
forecast_days = 2

# CSV Option
csv = True

# daytime between hours
start = 5 
end = 20

#taps aff temp
taps = 18
