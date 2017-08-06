import json
import os
import csv
import datetime
    
sakura = []
with open('../ueno_weather_db.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        sakura.append(row)
    
fuji = []  
with open('../fuji_db.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        fuji.append(row)
fuji_days = [datetime.datetime.strptime(row[0], '%Y/%m/%d') for row in fuji if int(row[1])]

sakura_bloom_day = 0
for row in sakura:
    if row[4] == min([i[4] for i in sakura], key=lambda x:abs(float(x) - 100)):
        sakura_bloom_day = datetime.datetime.strptime(row[0], '%Y/%m/%d')
        break


week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
yesno = ['No', 'YES!']

best_fuji_day = None
best_sakura_day = None
min_full_bloom_delta = 1000
for fuji_candidate_day in fuji_days:
    if fuji_candidate_day.weekday() == 5: #Saturday
        delta = 1
    elif fuji_candidate_day.weekday() == 6: #Sunday
        delta = -1
    else:
        continue
    sakura_candidate_day = fuji_candidate_day + datetime.timedelta(days = delta)
    full_bloom_delta = (sakura_candidate_day - sakura_bloom_day).days
    # print("Fuji day: {}{} {}".format(week[fuji_candidate_day.weekday()], fuji_candidate_day, yesno[fuji_candidate_day.weekday() >= 5]))
    # print("Sakura day: {}{} {}".format(week[sakura_candidate_day.weekday()], sakura_candidate_day, yesno[abs(full_bloom_delta) <= 3]))
    # print(full_bloom_delta)
    if abs(full_bloom_delta) < min_full_bloom_delta:
        min_full_bloom_delta = full_bloom_delta
        best_fuji_day = fuji_candidate_day
        best_sakura_day = sakura_candidate_day
    
if best_fuji_day and best_sakura_day and min_full_bloom_delta <= 3:
    print("Fuji day: {} {} {}".format(week[best_fuji_day.weekday()], best_fuji_day, yesno[best_fuji_day.weekday() >= 5]))
    print("Sakura day: {} {} {}".format(week[best_sakura_day.weekday()], best_sakura_day, yesno[abs(full_bloom_delta) <= 3]))
    
    fuji_dict = {'id': 1, 'year': best_fuji_day.year, 'month':best_fuji_day.month, 'day':best_fuji_day.day}
    sakura_dict = {'id': 2, 'year': best_sakura_day.year, 'month':best_sakura_day.month, 'day':best_sakura_day.day}
    
    if (best_fuji_day - best_sakura_day).days > 0:
        res = [sakura_dict, fuji_dict]
    else:
        res = [fuji_dict, sakura_dict]
else:
    res = []

print(json.dumps(res, indent=4, separators=(',', ': ')))


# print("fuji", fuji_days)
print("sakura", sakura_bloom_day)