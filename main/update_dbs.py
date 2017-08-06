import json
import requests
import json
import os
import csv
import datetime

darksky_api_key = ""
darksky_base_url = "https://api.darksky.net/forecast/{}/".format(darksky_api_key)

def get_daily_temp_forecast(lat_long):
    # Gets average daily temperature for one week
    darksky_url = darksky_base_url + "{},{}?extend=hourly&units=si".format(lat_long[0], lat_long[1])
    json_weather_darksky = requests.get(darksky_url).json()
    daily_temp = []
    hourly_sum = 0
    for i, forecast in enumerate(json_weather_darksky['hourly']['data']):
        temp_celsius = forecast['temperature']
        hourly_sum += temp_celsius
        if i % 24 == 23:
            daily_temp.append(hourly_sum/24)
            hourly_sum = 0
    return daily_temp

def get_daily_rain_forecast(lat_long):
    # Gets daily noon rainfall probability for one week
    darksky_url = darksky_base_url + "{},{}?extend=hourly&units=si".format(lat_long[0], lat_long[1])
    json_weather_darksky = requests.get(darksky_url).json()
    
    # daily_cloud_forecast = []
    daily_rain_forecast  = []
    for i, forecast in enumerate(json_weather_darksky['hourly']['data']):
        # cloud = forecast['cloudCover']
        rain = forecast['precipProbability']
        if i%24 == 12:
            daily_rain_forecast.append(rain)
            # daily_cloud_forecast.append(cloud)
            
    return daily_rain_forecast

def init_dbs():
    sakura = []
    with open('ueno_db_init.csv') as csv_in:
        reader = csv.reader(csv_in)
        for idx, row in enumerate(reader):
            if 1 < idx:
                sakura.append(row)
    with open('ueno_db.csv', 'w') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerows(sakura)
        
    fuji = []
    with open('fuji_db_init.csv') as csv_in:
        reader = csv.reader(csv_in)
        for idx, row in enumerate(reader):
            if 1 < idx:
                fuji.append(row)
    with open('fuji_db.csv', 'w') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerows(fuji)

def update_dbs(current_time):
    ## UENO
    # Load DB
    sakura = []
    with open('ueno_db.csv') as csv_in:
        reader = csv.reader(csv_in)
        for idx, row in enumerate(reader):
            sakura.append(row)
    
    # Update forecast
    ueno_coords = [35.715784, 139.773589]
    ueno_temp_forecast = get_daily_temp_forecast(ueno_coords)
    ueno_rain_forecast = get_daily_rain_forecast(ueno_coords)
    # ueno_temp_forecast = [29.132916666666663, 28.523333333333337, 27.904166666666665, 29.236666666666668, 28.540833333333335, 28.8025, 27.929166666666664]
    # ueno_rain_forecast = [0, 0.35, 0, 0, 0, 0, 0]

    prev_temp = 0
    prev_max_temp = 0
    prev_cum_max_temp = 0
    prev_cum_temp_bloomed = 0
    for idx in range(len(sakura)):
        row = sakura[idx]
        date,temp,max_temp,cum_max_temp,cum_temp_bloom,bloomed,rain = row
        date = datetime.datetime.strptime(date, '%Y/%m/%d')
        
        # Update forecast
        delta_days = (date - current_time).days
        if 1 <= delta_days <= 7:
            temp = "{:.1f}".format(ueno_temp_forecast[delta_days - 1])
            max_temp = "{:.1f}".format(4.1 + 1.1*ueno_temp_forecast[delta_days - 1]) #Linear relation from past trend
            rain = "{:.2f}".format(ueno_rain_forecast[delta_days - 1])
        
        # Update cumulative temperatures
        cum_max_temp = "{:.1f}".format(float(prev_cum_max_temp) + float(max_temp))
        cum_temp_bloom = "{:.1f}".format((float(prev_cum_temp_bloomed) + float(temp) * float(bloomed)) * float(bloomed))
        prev_temp = temp
        prev_max_temp = max_temp
        prev_cum_max_temp = cum_max_temp
        prev_cum_temp_bloomed = cum_temp_bloom
        
        date = datetime.datetime.strftime(date, '%Y/%m/%d')
        row = [date,temp,max_temp,cum_max_temp,cum_temp_bloom,bloomed,rain]
        sakura[idx] = row
    
    # Save DB
    with open('ueno_db.csv', 'w') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerows(sakura)
        
    ## FUJI
    # Load DB
    fuji = []
    with open('fuji_db.csv') as csv_in:
        reader = csv.reader(csv_in)
        for idx, row in enumerate(reader):
            fuji.append(row)
    
    # Update forecast
    fuji_coords = [35.3402621,138.5545061]
    fuji_rain_forecast = get_daily_rain_forecast(fuji_coords)
    # print(fuji_rain_forecast)
    # fuji_rain_forecast = [0, 0.57, 0.08, 0.1, 0.1, 0.05, 0]

    for idx in range(len(fuji)):
        row = fuji[idx]
        date, recommended = row
        date = datetime.datetime.strptime(date, '%Y/%m/%d')
        
        # Update forecast
        delta_days = (date - current_time).days
        if 1 <= delta_days <= 7:
            rain = fuji_rain_forecast[delta_days - 1]
            recommended = 1 if (rain < 0.3) else 0
            
        date = datetime.datetime.strftime(date, '%Y/%m/%d')
        row = [date, recommended]
        fuji[idx] = row
        
    # Save DB
    with open('fuji_db.csv', 'w') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerows(fuji)

if __name__ == '__main__':
    now = datetime.datetime.strptime('2017/3/22', '%Y/%m/%d') # datetime.datetime.now()

    init_dbs()
    update_dbs(now)
    
    # ueno_coords = [35.715784, 139.773589]
    # print(get_daily_rain_forecast(ueno_coords))
