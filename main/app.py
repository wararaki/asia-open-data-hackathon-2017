from flask import Flask, render_template, request
import json
import os
import csv
import datetime

app = Flask(__name__)

def fix_view_data(data, dates):
    tmp_dates = json.loads(dates)
    for dt in tmp_dates:
        for i in range(len(data['contents'])): #range(len(list(data.keys()))):
            #print(dt)
            #print(data[i]['id'])
            if dt['id'] == data['contents'][i]['id']:
                data["contents"][i]['datetime'] = "{0:04d}年{1:02d}月{2:02d}日".format(dt['year'], dt['month'], dt['day'])
                break
            #data[i] = dt
    return data

@app.route("/")
def home():
    with open("./static/content_list.json", "r") as f:
        data = json.load(f)
    data = fix_view_data(data, recommend_fuji_ueno()[0])
    return render_template("hello.html", data=data)


@app.route("/book")
def book():
    with open("./static/content_list.json", "r") as f:
        data = json.load(f)
    data = fix_view_data(data, recommend_fuji_ueno()[0])
    return render_template("book.html", data=data)


@app.route("/api/test")
def recommend_test():
    res = {
        '3/2': ['ueno', 'fuji'],
        '3/3': ['ueno', 'fuji'],
        '3/4': ['ueno']
    }
    return json.dumps(res)
    
@app.route('/api/v1')
def recommend():
    sakura = []
    with open('ueno_db.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            sakura.append(row)
        
    fuji = []  
    with open('fuji_db.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            fuji.append(row)
    
    sakura_bloom_day = 0
    for row in sakura:
        if row[4] == min([i[4] for i in sakura], key=lambda x:abs(float(x) - 100)):
            sakura_bloom_day = datetime.datetime.strptime(row[0], '%Y/%m/%d')
            break

    sakura_days = [sakura_bloom_day + datetime.timedelta(days=n) for n in range(-3,4)]
    sakura_list_of_dict = [{'id': 0, 'year': i.year, 'month':i.month, 'day':i.day} for i in sakura_days]
    
    fuji_days = [datetime.datetime.strptime(row[0], '%Y/%m/%d') for row in fuji if int(row[1])]
    fuji_list_of_dict = [{'id': 1, 'year': i.year, 'month':i.month, 'day':i.day} for i in fuji_days]
    
    res = [fuji_list_of_dict[0], sakura_list_of_dict[0]]
    return json.dumps(res)

@app.route('/api/fuji+ueno')
@app.route('/api/ueno+fuji')
def recommend_fuji_ueno():
    sakura = []
    with open('ueno_db.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            sakura.append(row)
        
    fuji = []  
    with open('fuji_db.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            fuji.append(row)
    
    for row in sakura:
        if row[4] == min([i[4] for i in sakura], key=lambda x:abs(float(x) - 100)):
            sakura_bloom_day = datetime.datetime.strptime(row[0], '%Y/%m/%d')
            break

    fuji_days = [datetime.datetime.strptime(row[0], '%Y/%m/%d') for row in fuji if int(row[1])]

    # week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # yesno = ['No', 'YES!']
    
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
        if abs(full_bloom_delta) < min_full_bloom_delta:
            min_full_bloom_delta = full_bloom_delta
            best_fuji_day = fuji_candidate_day
            best_sakura_day = sakura_candidate_day
        
    if best_fuji_day and best_sakura_day and min_full_bloom_delta <= 3:
        # print("Fuji day: {} {} {}".format(week[best_fuji_day.weekday()], best_fuji_day, yesno[best_fuji_day.weekday() >= 5]))
        # print("Sakura day: {} {} {}".format(week[best_sakura_day.weekday()], best_sakura_day, yesno[abs(full_bloom_delta) <= 3]))
        
        fuji_dict = {'id': 1, 'year': best_fuji_day.year, 'month':best_fuji_day.month, 'day':best_fuji_day.day}
        sakura_dict = {'id': 2, 'year': best_sakura_day.year, 'month':best_sakura_day.month, 'day':best_sakura_day.day}
    
        if (best_fuji_day - best_sakura_day).days > 0:
            res = [sakura_dict, fuji_dict]
        else:
            res = [fuji_dict, sakura_dict]
    
    else:
        res = []

    return json.dumps(res, indent=4, separators=(',', ': ')) , 200, {'Content-Type': 'text'}

@app.route('/api/ueno')
def recommend_ueno():
    sakura = []
    with open('ueno_db.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            sakura.append(row)

    for row in sakura:
        if row[4] == min([i[4] for i in sakura], key=lambda x:abs(float(x) - 100)):
            sakura_bloom_day = datetime.datetime.strptime(row[0], '%Y/%m/%d')
            break

    # week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    # yesno = ['No', 'YES!']
    
    best_sakura_day = None
    for delta in range(-3,4):
        sakura_candidate_day = sakura_bloom_day + datetime.timedelta(days = delta)
        if sakura_candidate_day.weekday() >= 5: #Saturday or Sunday
            best_sakura_day = sakura_candidate_day
            sakura_dict = {'id': 2, 'year': best_sakura_day.year, 'month':best_sakura_day.month, 'day':best_sakura_day.day}
            break
    
    if best_sakura_day:
        res = [sakura_dict]
    else:
        res = []

    return json.dumps(res, indent=4, separators=(',', ': ')) , 200, {'Content-Type': 'text'}

@app.route('/api/fuji')
def recommend_fuji():
    fuji = []  
    with open('fuji_db.csv') as f:
        reader = csv.reader(f)
        for row in reader:
            fuji.append(row)

    fuji_days = [datetime.datetime.strptime(row[0], '%Y/%m/%d') for row in fuji if int(row[1])]

    best_fuji_day = None
    for fuji_candidate_day in fuji_days:
        if fuji_candidate_day.weekday() >= 5:  #Saturday or Sunday
            best_fuji_day = fuji_candidate_day
            fuji_dict = {'id': 1, 'year': best_fuji_day.year, 'month':best_fuji_day.month, 'day':best_fuji_day.day}
            break
    
    if best_fuji_day:
        res = [fuji_dict]
    else:
        res = []

    return json.dumps(res, indent=4, separators=(',', ': ')) , 200, {'Content-Type': 'text'}


if __name__ == '__main__':
	app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
