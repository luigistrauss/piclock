import os, sys, json, requests, time, csv
from datetime import datetime
from lib.waveshare_epd import epd3in7
from PIL import Image, ImageDraw, ImageFont
import settings as settings
import Adafruit_DHT

# Raspberry Pi with DHT sensor - connected Pin 27
sensor = sensor = Adafruit_DHT.DHT11
pin = 27

#Define directories
pic_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
icon_dir = os.path.join(pic_dir, 'weather_icons')
font_dir = os.path.join(pic_dir, 'font')

#Display driver
epd = epd3in7.EPD()
w = epd.height
h = epd.width

#CSV Option
CSV_OPTION = settings.csv

# define funciton for writing image and sleeping for 5 min.
def write_to_screen(image, sleep_seconds):
    print('Writing to screen.')
    # Write to screen
    epd.Clear(0,0)
    h_image = Image.new('1', (w,h), 255)
    # Open the template
    screen_output_file = Image.open(os.path.join(pic_dir, image))
    # Initialize the drawing context with template as background
    h_image.paste(screen_output_file, (0, 0))
    epd.display_1Gray(epd.getbuffer(h_image))
    # Sleep
    print('Sleeping for ' + str(sleep_seconds) +'.')
    time.sleep(sleep_seconds)

# define function for displaying error
def display_error(error_source):
    # Display an error
    print('Error in the', error_source, 'request.')
    # Initialize drawing
    error_image = Image.new('1', (w, h), 255)
    # Initialize the drawing
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), error_source +' ERROR', font=font48, fill=black)
    draw.text((100, 300), 'Retrying in 30 seconds', font=font24, fill=black)
    current_time = datetime.now().strftime('%H:%M')
    draw.text((300, 365), 'Last Refresh: ' + str(current_time), font = font48, fill=black)
    # Save the error image
    error_image_file = 'error.png'
    error_image.save(os.path.join(pic_dir, error_image_file))
    # Close error image
    error_image.close()
    # Write error to screen 
    write_to_screen(error_image_file, 30)

#set fonts & colours
font12 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 12)
font16 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 16)
font18 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 18)
font22 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 22)
font24 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 24)
font30 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 30)
font36 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 36)
font48 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 48)
font60 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 60)
font72 = ImageFont.truetype(os.path.join(font_dir, 'Roboto-Black.ttf'), 72)
black = 'rgb(0,0,0)'
white = 'rgb(255,255,255)'
grey1 = 0x80

# Initialise & clear screen
print('Initializing and clearing screen.')
epd.init(0)
epd.Clear(0,0)


while True:
    # get local readings
    print('Reading local temp & humidity')
    count, readingCount, avgTemp, avgHumidity = [ 0, 0, 0, 0 ]
    while (count < 10):
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            if humidity is not None and temperature is not None:
                avgTemp = avgTemp + temperature
                avgHumidity = avgHumidity + humidity
                readingCount = readingCount + 1
            count = count + 1
    insideTemp = int(avgTemp / readingCount)
    insideHumidity = int(avgHumidity / readingCount)
    """
    print(insideTemp)
    print(insideHumidity)
    """
    # Ensure there are no errors with connection
    error_connect = True
    while error_connect == True:
        try:
            # HTTP request
            print('Attempting to connect to Weatherbit.')
            response = requests.get(f"{settings.currentWeatherAPIURL}?key={settings.weatherAPIKey}&lat={settings.latitude}&lon={settings.longitude}")
            print('Initial connection successful.')
            error_connect = None
        except:
            # Call function to display connection error
            print('Connection error.')
            display_error('CONNECTION') 

    error = None
    while error == None:
        # Check status of code request
        if response.status_code == 200:
            print('Connection to forecasts successful.')
        # Get json data from current/Daily/minutely forecast
            current = requests.get(
                f"{settings.currentWeatherAPIURL}?key={settings.weatherAPIKey}&lat={settings.latitude}&lon={settings.longitude}"
                ).json()
            daily = requests.get(
                f"{settings.dailyWeatherAPIURL}?key={settings.weatherAPIKey}&lat={settings.latitude}&lon={settings.longitude}&days={settings.forecast_days}"
                ).json()
            minutely = requests.get(
                f"{settings.minutelyWeatherAPIURL}?key={settings.weatherAPIKey}&lat={settings.latitude}&lon={settings.longitude}"
                ).json()

            currentData = current['data'][0]
            dailyData = daily['data'][0]
            minutelyData = minutely['data'][0]
            summary = currentData['weather']

            #Define weather variables
            temp = currentData['temp']
            feelsLikeTemp = currentData['app_temp']
            humidity = currentData['rh']    
            windSpeed = currentData['wind_spd']
            windDir = currentData['wind_cdir']
            cloudCover = currentData['clouds']
            precipProbability = dailyData['pop']
            precip = dailyData['precip']
            partOfDay = currentData['pod']
            icon = summary['icon']
            code = summary['code']
            description = summary['description']
            apparentTempMin = dailyData['min_temp']
            apparentTempMax = dailyData['max_temp']
            currentPrecip = minutelyData['precip']
            currentSnow = minutelyData['snow']
            airQuality = currentData['aqi']
            
            if (len(description) >= 17):
                description = description[0:16] + '.'

            #Append weather data to CSV if csv_option == True
            if CSV_OPTION == True:
                #Get current date & time
                current_date = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                # open csv file and append weather data
                with open('/home/pi/weather_records.csv', 'a', newline='') as csv_file:
                    writer = csv.writer(csv_file, delimiter=';')
                    writer.writerow([current_date, settings.locationName, temp, feelsLikeTemp, apparentTempMin, apparentTempMax, insideTemp, 
                                      humidity, insideHumidity, currentPrecip, windSpeed, windDir])
                print('Weather data appended to CSV')
            
            #Get if current time is day or night
            def day_time():
                h = datetime.now().hour
                if settings.start <= h <= settings.end:
                    return True
                return False
            daytime = day_time()

            #Set taps aff/on
            def taps_aff(temp):
                if temp >= settings.taps:
                    return "AFF"
                return " ON"
            tapsaff = taps_aff(temp)

            #Strings to be printed to screen
            string_location = settings.locationName
            string_temp_current = format(temp, '.1f') + u'\N{DEGREE SIGN}C'
            string_feels_like = "Feels like: " + format(feelsLikeTemp, '.1f') + u'\N{DEGREE SIGN}C'
            string_temp_inside = "Inside Temp: " + format(insideTemp, '.1f') + u'\N{DEGREE SIGN}C'
            string_humidity = "Humidity: " + str(humidity) + '%'
            string_inside_humidity = "Inside Humidity: " + str(insideHumidity) + '%'
            string_wind = "Wind: " + format(windSpeed, '.1f') + ' m/s ' +format(windDir)
            string_report = description.title()
            string_temp_max = "High: " + format(apparentTempMax, '>.1f') + u'\N{DEGREE SIGN}C'
            string_temp_min = "Low: " + format(apparentTempMin, '>.1f') + u'\N{DEGREE SIGN}C'
            string_precip_percent = "Precipitation: " + str(format(precipProbability, '.0f')) + '%'
            string_air_quality = "Air Quality Index: " + format(airQuality, '>.0f')
            string_taps = str(tapsaff)

            #set error code to false
            error = False

            """print(string_location)
            print(string_temp_current)
            print(string_feels_like)
            print(string_humidity)
            print(string_wind)
            print(string_report)
            print(string_temp_max)
            print(string_temp_min)
            print(string_precip_percent)
            print(string_air_quality) """

        else:
            # Call function to display HTTP error
            display_error('HTTP')

    def code_to_icon(code):
        if 200 <= code < 234:
            return "thunder-storm"
        elif 300 <= code < 303:
            return "little-rain"
        elif 500 <= code < 521:
            return "rain"
        elif code == 521:
            return "little-rain"
        elif code == 522:
            return "rainy-umbrella"
        elif code == 600 or code == 623:
            return "little-snow"
        elif code == 601 or code == 621:
            return "snow"
        elif code == 602 or code == 622:
            return "snow-storm"
        elif 610 <= code < 613:
            return "sleet"
        elif 700 <= code < 721 or 740 < code < 752 and daytime:
            return "fog-day"
        elif 700 <= code < 721 or 740 < code < 752 and not daytime:
            return "fog-night"
        elif code == 731:
            return "dust"
        elif code == 800 and daytime:
            return "sun"
        elif code == 800 and not daytime:
            return "moon"
        elif 801 <= code < 804 and daytime:
            return "partly-cloudy-day"
        elif 801 <= code < 804 and not daytime:
            return "partly-cloudy-night"
        elif code == 804:
            return "darkclouds"
        else:
            return "cloudy"

    """print(code_to_icon(code))"""
        

    # Open template file
    template = Image.open(os.path.join(pic_dir, 'template.png'))
    draw = ImageDraw.Draw(template)

    # Draw top left box
    ## Open icon file:
    icon_file = code_to_icon(code) + '.jpg'
    icon_image = Image.open(os.path.join(icon_dir, icon_file))
    ##Paste the image
    template.paste(icon_image, (10, 5))
    ##Draw Text
    draw.text((10, 118), string_report, font=font16, fill=black)
    draw.text((10, 132), string_precip_percent, font=font16, fill=grey1)
    ##Draw top right box
    draw.text((210, 15), string_temp_current, font=font72, fill=black)
    draw.text((220, 90), string_feels_like, font=font24, fill=grey1)
    draw.text((220, 110), string_temp_inside, font=font22, fill=grey1)
    # Draw bottom left box
    #draw.text((10, 180), string_temp_max, font=font24, fill=black)
    draw.text((35, 180), 'TAPS:', font=font24, fill=grey1)
    #draw.line((10,370, 40,370), fill=black)
    #draw.text((10, 220), string_temp_min, font=font24, fill=black)
    draw.text((20, 210), string_taps, font=font48, fill=black) 
    # Draw bottom middle box
    draw.text((200, 170), string_humidity, font=font18, fill=black)
    draw.text((170, 190), string_inside_humidity, font=font18, fill=grey1)
    draw.text((190, 210), string_wind, font=font18, fill=black)
    draw.text((170, 230), string_air_quality, font=font18, fill=grey1)
    # Draw bottom right box
    draw.text((375, 180), 'UPDATED', font=font18, fill=white)
    current_time = datetime.now().strftime('%H:%M')
    draw.text((365, 200), current_time, font = font36, fill=white)
    draw.text((390, 240), string_location, font = font24, fill=white)

    # Save the image for display as PNG
    screen_output_file = os.path.join(pic_dir, 'screen_output.png')
    template.save(screen_output_file)
    # Close the template file
    template.close()

    # Refresh clear screen to avoid burn-in at 3:00 AM
    if datetime.now().strftime('%H') == '03':
        print('Clearning screen to avoid burn-in.')
    	epd.Clear(0,0)

    # Write to screen
    write_to_screen(screen_output_file, 600)
