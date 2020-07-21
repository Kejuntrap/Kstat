from flask import Flask
from bs4 import BeautifulSoup
from urllib import request
import hashlib
import hmac
import array
import requests
import os
from os.path import join, dirname
from dotenv import load_dotenv
import json
import datetime

dotenv_path = join(dirname(__file__), 'keys.env')
load_dotenv(dotenv_path)

prefs_vol = 9
cities_vol = 21
trains_vol = 33

app = Flask(__name__)

@app.route('/')
def hello():
    name = "Hello World"
    return name

@app.route('/good')
def good():
    name = "Good"
    return name


@app.route('/fukuokadam')
def fukuokadam():
    url = 'https://ckan.open-governmentdata.org/dataset/8c753941-a47e-43de-b438-30f159c6efda/resource/96b18b76-f2aa-47a8-9530-255d439a0090/download/realtimetotal.html'
    response = request.urlopen(url)
    soup = BeautifulSoup(response)
    response.close()
    a = soup.find_all("span", class_="number")

    for i in range(7):
        a[i] = a[i].text

    message = a[0]+"年"+a[1]+"月"+a[2]+"日"+a[3]+"時時点の福岡県福岡市の全ダム貯水率は" +a[5]+"%です(前日比: "+a[6]+"%)"
    return message

@app.route('/kyusyudensya')
def kyusyudensya():
    url = 'https://www.tetsudo.com/traffic/category/%E4%B9%9D%E5%B7%9E%E3%82%A8%E3%83%AA%E3%82%A2/'
    response = request.urlopen(url)
    soup = BeautifulSoup(response)
    response.close()
    a = soup.find_all("span", class_="display-desktop")
    rails = ['地下鉄空港線・箱崎線','七隈線','博多南線','山陽本線','鹿児島本線','香椎線','福北ゆたか線','三角線','肥薩線','指宿枕崎線','長崎本線','唐津線','筑肥線','佐世保線','大村線','久大本線','豊肥本線','日豊本線','日田彦山線','日南線','宮崎空港線','吉都線','筑豊本線','後藤寺線','西鉄天神大牟田線','貝塚線','北九州モノレール','甘木鉄道','松浦鉄道','肥薩おれんじ鉄道','ゆいレール','島原鉄道','南阿蘇鉄道']
    message=""
    for i in range(trains_vol):
        a[i] = a[i].text
        if 'あり' in a[i]:
            a[i] = "delay"
        else:
            a[i] = "none"

        if a[i] == "delay" and i != 24:
            message=message+(f"**{rails[i]}:遅延あり**\n")
        elif a[i] == "delay" and i == 24:
            message=message+(f"**{rails[i]}:遅延あり 危機的状況**:alert:\n")
    if message == '':
        message = '遅延は確認されていません'
    return message

@app.route('/kyusyutenki')
def kyusyutenki():
    key = os.environ.get("SECURE").encode("utf-8")
    wt = os.environ.get("WAPIKEY")
    pref = ['山口','福岡','佐賀','長崎','大分','熊本','宮崎','鹿児島','沖縄']
    city = [
        ['Shimonoseki'],
        ['Fukuoka' , 'Iizuka'],
        ['Saga'],
        ['Tsushima' ,'Fukuecho','Nagasaki' ],
        ['Hita','Oita'],
        ['Kumamoto','Yatsushiro'],
        ['Miyakonojo','Miyazaki','Nobeoka'],
        ['Aira','Ibusuki','Kanoya','Naze'],
        ['Kunigami','Naha','Ishigaki'],
    ]

    disp = [
        ['下関'],
        ['福岡','飯塚'],
        ['佐賀'],
        ['対馬','福江','長崎'],
        ['日田','大分'],
        ['熊本','八代'],
        ['都城','宮崎','延岡'],
        ['姶良','指宿','鹿屋','名瀬'],
        ['国頭','那覇','石垣'],
    ]

    weatherlist={
        "Thunderstorm":":thunder_cloud_rain:",
        "Clouds":":cloud:",
        "Drizzle":":cloud_rain:",
        "Rain":":umbrella:",
        "Snow":":snowman:",
        "Clear":":sunny:",
        "Mist":":fog:",
        "Smoke":":fog:",
        "Haze":":fog:",
        "Dust":":fog:",
        "Fog":":fog:",
        "Sand":":fog:",
        "Ash":":fog:",
        "Squall":":umbrella:",
        "Tornado":":cyclone:"
        }

    postcontent=""
    for g in range(prefs_vol):
        postcontent=f"{postcontent}## {pref[g]}\n"
        for h in range(len(city[g])):
            url = f'http://api.openweathermap.org/data/2.5/forecast?q={city[g][h]},jp&APPID={wt}'
            response = requests.get(url)
            data = response.json()
            jsonText = json.loads(json.dumps(data, indent=4))
            region = disp[g][h]
            content = f"|{region}|" #一時投稿内容
            tempary=[0]*5
            weastam=[""]*5
            for i in range(5):      # 0ji 6ji 12ji 18ji 24ji の5つ
                weli = jsonText["list"][i * 2]
                tim = str(datetime.datetime.fromtimestamp(weli["dt"]))[11:-3]   #時間
                content=f"{content}{tim}|"
                tempary[i] = int((weli["main"]["temp"]-273.15+0.99)//1)    #温度
                weastam[i] = weatherlist[weli["weather"][0]["main"]]   #天気に対応するスタンプ

            content=f"{content}\n|"

            for i in range(6):
                content=f"{content}---|"

            content=f"{content}\n|温度|"

            for i in range(5):
                content=f"{content}{tempary[i]}|"
            
            content=f"{content}\n|天気|"

            for i in range(5):
                content=f"{content}{weastam[i]}|"

            content=f"{content}\n\n"
            postcontent=f"{postcontent}{content}"
    return postcontent

@app.route('/kazehaminamikara')
def kazehaminamikara():
    key = os.environ.get("SECURE").encode("utf-8")
    wt = os.environ.get("WAPIKEY")
    lat = 31.59
    lon = 130.66       #桜島の座標
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&APPID={wt}"
    response = requests.get(url)
    data = response.json()
    jsonText = json.loads(json.dumps(data, indent=4))
    windmuki = ["北","北北東","北東","東北東","東","東南東","南東","南南東","南","南南西","南西","西南西","西","西北西","北西","北北西"]
    citymuki = ["指宿","指宿","鹿児島","鹿児島","鹿児島","鹿児島","川内","川内","姶良・霧島","姶良・霧島","姶良・霧島","垂水・鹿屋","垂水・鹿屋","垂水・鹿屋","垂水・鹿屋","垂水・鹿屋"]
    content = "桜島の降灰方向予測は\n"
    content = f'{content}|時間|風速(m/s)|方向(風向)|\n|---|---|---|\n'

    for i in range(min(len(jsonText["list"]),9)):
        tim = str(datetime.datetime.fromtimestamp(jsonText["list"][i]["dt"]))[11:-3]
        deg = jsonText["list"][i]["wind"]["deg"]
        spd = int(float(jsonText["list"][i]["wind"]["speed"])+0.5)
        dirc = ((int(deg)+11)*2//45)%16
        if spd > 0:
            content=f'{content}|{tim}|{spd}|{citymuki[dirc]}方向|\n'
        elif spd == 0:
            content=f'{content}|{tim}|0|なし|\n'
    return content

@app.route('/chikugogawa')
def chikugogawa():
    pref_cnt = 2
    url = [[],[]]
    url[0] = 'https://www.river.go.jp/kawabou/ipSuiiGaikyo.do?init=init&areaCd=89&prefCd=4301&townCd=&gamenId=01-0902&fldCtlParty=no'
    url[1] = 'https://www.river.go.jp/kawabou/ipSuiiGaikyo.do?init=init&areaCd=89&prefCd=4001&townCd=&gamenId=01-0902&fldCtlParty=no'
    place = ['小国','うきは','田主丸','高良','大川','イオン小郡(宝満川)']
    a = [[""] , [""] ]   #熊本、福岡、佐賀

    for h in range(pref_cnt):
        response = request.urlopen(url[h])
        soup = BeautifulSoup(response)
        response.close()
        a[h] = soup.find_all("td", class_="tb1td2Right")
        print(len(a[h]))
        for _ in range(len(a[h])):
            a[h][_] = a[h][_].text
            a[h][_] = a[h][_].replace(' ','')
            a[h][_] = a[h][_].replace('\t','')
            a[h][_] = a[h][_].replace('\n','')
            a[h][_] = a[h][_].replace('　','')
            a[h][_] = a[h][_].replace('\r','')
    res=[[""] ,[""] ,[""] ,[""] ,[""],[""]]
    res[0] = a[0][10:15]
    res[1] = a[1][170:175]
    res[2] = a[1][180:185]
    res[3] = a[1][220:225]
    res[4] = a[1][190:195]
    res[5] = a[1][210:215]

    content = "|場所|水位|:ok:|:exclamation:|:alert:|:innocent:|\n|---|---|---|---|---|---|\n"
    ampo = '$\Huge{'
    ampc = '}$'
    for i in range(len(res)):
        if float(res[i][0]) > float(res[i][4]):
            tmp = f"|{ampo}{place[i]}{ampc}|"
        else:
            tmp = f"|{place[i]}|"
        for j in range(5):
            if j == 0:
                if float(res[i][0]) > float(res[i][4]):
                    tmp = f'{tmp}{ampo}{res[i][j]}{ampc}|'
                else:
                    tmp = f'{tmp}{res[i][j]}|'
            else:
                tmp = f'{tmp}{res[i][j]}|'
        tmp = f'{tmp}\n'
        content = f'{content}{tmp}'
    return content

@app.route('/pm25')
def pm25():
    base = 35 #基準値（国の）
    prefs=["福岡"]
    placename = [
        ["福岡","久留米","飯塚","北九州"],
    ]
    placeid = [
        ["40133010","40203100","40205010","40106010"],
    ]
    unit = '\\rm{\mu g/m^3}'
    content=f"PM2.5飛散量(${unit}$)\n基準値:$35{unit}$未満\n"
    for h in range(len(prefs)):
        content = f'{content}### {prefs[h]}\n'
        content = f'{content}|場所|飛散量(${unit}$)|\n|---|---|\n'
        for i in range(len(placeid[h])):
            url = f'https://pm25.jp/r/{placeid[h][i]}/'
            response = request.urlopen(url)
            soup = BeautifulSoup(response)
            response.close()
            a = soup.find_all("b")
            for j in range(len(a)):
                a[j] = a[j].text
            if int(a[0]) >= base:
                content=f'{content}|{placename[h][i]}|{a[0]}:alert:|\n'
            else:
                content=f'{content}|{placename[h][i]}|{a[0]}|\n'
            #print(a)
    return content


## おまじない
if __name__ == "__main__":
    app.run(debug=True)
