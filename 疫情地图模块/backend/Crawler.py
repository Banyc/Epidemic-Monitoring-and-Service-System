from bs4 import BeautifulSoup
import requests
import random
from user import user
import time
import re
import json
import datetime
import socket
import copy

class Crawler:
    def __init__(self):
        #获取当前ip
        hostname = socket.gethostname()
        self.ip = socket.gethostbyname(hostname)
        # 爬虫
        self.session = requests.session()
        self.crawl_timestamp = int()
        self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.yesterday=(datetime.date.today()- datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        self.ChinaMap=[]
        self.ForeignMap=[]

    # 更新
    def run(self):
         #self.age(); #提交年龄数据
         #self.sex(); #提交性别数据


        while True:
        #try:
            self.crawler()
            # 爬取新数据
            time.sleep(60 * 30)  # 30分钟更新数据
        #except BaseException:
            #continue


    # 爬取信息
    def crawler(self):
        while True:
            # 若爬取间隔过短，连接时需要更新用户信息
            self.session.headers.update(
                {
                    'user-agent': random.choice(user)
                }
            )
            self.crawl_timestamp = int(time.time() * 1000)
            # 连接
            try:
                r = self.session.get(url='https://ncov.dxy.cn/ncovh5/view/pneumonia')
            except requests.exceptions.ChunkedEncodingError:
                continue
            soup = BeautifulSoup(r.content, 'html.parser')

            area_information = re.search(r'\[(.*)\]', str(soup.find('script', attrs={'id': 'getAreaStat'})))
            if area_information:
                self.area_parser(area_information=area_information)

            abroad_information = re.search(r'\[(.*)\]',
                                           str(soup.find('script', attrs={'id': 'getListByCountryTypeService2true'})))
            if abroad_information:
                 self.abroad_parser(abroad_information=abroad_information)

            # 重新获取
            if not area_information or not abroad_information:
                time.sleep(3)
                continue
            break

        print('Successfully crawled.')

    # 国内信息
    def area_parser(self, area_information):
        area_information = json.loads(area_information.group(0))
        # print(area_information)
        for area in area_information:
            if len(area['cities']) == 0:
                #直辖市或地区
                self.ChinaMap.append({
                    "Data": self.date,
                    "Province": area[ 'provinceShortName'],
                    "City": area[  'provinceShortName'],
                    "increaseDiagnosis":-10000,
                    "increaseDeath":-10000,
                    "increaseCure":-10000,
                    "increaseSuspected":-10000,
                    "totalDiagnosis":area['confirmedCount'],
                    "totalDeath":area['deadCount'],
                    "totalCure":area[ 'curedCount'],
                    "totalSuspected":area['suspectedCount'],
                    "extanceDiagnosis":area['currentConfirmedCount'],
                    "extanceSuspected":0,
                    "id":area[ 'locationId'],
                    "Return":None
                })
                continue
            else:
                #省份总信息
                self.ChinaMap.append({
                    "Data": self.date,
                    "Province": area['provinceShortName'],
                    "City": area['provinceShortName'],
                    "increaseDiagnosis": -10000,
                    "increaseDeath": -10000,
                    "increaseCure": -10000,
                    "increaseSuspected": -10000,
                    "totalDiagnosis": area['confirmedCount'],
                    "totalDeath": area['deadCount'],
                    "totalCure": area['curedCount'],
                    "totalSuspected": area['suspectedCount'],
                    "extanceDiagnosis": area['currentConfirmedCount'],
                    "extanceSuspected": 0,
                    "id": area['locationId'],
                    "Return":None
                })
                #城市
                for city in area[ 'cities']:
                    t={
                        "Data": self.date,
                        "Province": area['provinceShortName'],
                        "City": city['cityName'],
                        "increaseDiagnosis": 0,
                        "increaseDeath": 0,
                        "increaseCure": 0,
                        "increaseSuspected": 0,
                        "totalDiagnosis": city['confirmedCount'],
                        "totalDeath": city['deadCount'],
                        "totalCure": city['curedCount'],
                        "totalSuspected": city['suspectedCount'],
                        "extanceDiagnosis": city['currentConfirmedCount'],
                        "extanceSuspected": 0,
                        "id": city['locationId'],
                        "Return":None
                    }
                    #北京卫健委未明确大部分治愈与死亡病例的分区归属，因此北京市下辖分区的现存确诊暂无法获取
                    if t["Province"]=="北京":
                        t["extanceDiagnosis"]=-10000

                    self.ChinaMap.append(t)
        #print(self.ChinaMap)

        # 提交
        headers = {
            "content-type": "application/json; charset=UTF-8",
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'
        };
        print("China")
        for item in self.ChinaMap:
            # 查询数据
            checkQuery = {
                "Data": item["Data"],
                "City": item['City'],
                "Return": 'singleCity'
            }
            LastQuery={
                "Data": self.yesterday,
                "City": item['City'],
                "Return": 'singleCity'
            }


            # 每日新增数目
            data = (json.dumps(LastQuery, ensure_ascii=False)).encode('utf-8')
            checkres = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/select',
                                     data=data, headers=headers)
            last=json.loads(checkres.content)
            print(last['result'], last['message'])
            if last['result'] == 'Y' and 'extance' in last['message'].keys() and last['message']['extance']!=None:
                item['increaseDiagnosis']=item['extanceDiagnosis']-last['message']['extance']['confirmedNumber']
            if last['result'] == 'Y' and 'total' in last['message'].keys() and last['message']['total'] != None:
                item['increaseDeath'] = item['totalDeath'] - last['message']['total']['deathToll']
                item['increaseCure'] = item['totalCure'] - last['message']['total']['cureNumber']
            print("increaseDiagnosis:",item['increaseDiagnosis'])
            print("increaseDeath:", item['increaseDeath'])
            print("increaseCure:", item['increaseCure'])

            #查询数据是否存在
            data = (json.dumps(checkQuery, ensure_ascii=False)).encode('utf-8')
            checkres = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/select',
                                     data=data, headers=headers)
            result = json.loads(checkres.content)
            print(result)

            print(item)
            # 提交数据
            # total
            item["Return"] = "total"
            city = json.dumps(item, ensure_ascii=False)
            if result['result'] == 'Y' and 'total' in result['message'].keys() and result['message']['total']!=None:
                # update
                print("update total")
                res = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/update', data=city.encode('utf-8'),
                                    headers=headers)
            else:
                # insert
                print("insert total")
                res = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/insert', data=city.encode('utf-8'),
                                    headers=headers)
            print(res.text)

            # increase
            item['Return']='newAddtion'
            city = json.dumps(item, ensure_ascii=False)
            if result['result'] == 'Y' and 'newAddtion' in result['message'].keys() and result['message']['newAddtion']!=None:
                # update
                print("update increase")
                res = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/update', data=city.encode('utf-8'),
                                    headers=headers)
            else:
                # insert
                print("insert increase")
                res = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/insert', data=city.encode('utf-8'),
                                    headers=headers)
            print(res.text)

            # exsisting
            item['Return']='extance'
            city = json.dumps(item, ensure_ascii=False)
            if result['result'] == 'Y' and 'extance' in result['message'].keys() and result['message']['extance']!= None:
                # update
                print("update")
                res = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/update', data=city.encode('utf-8'),
                                    headers=headers)
            else:
                # insert
                print("insert")
                res = requests.post(url='http://127.0.0.1:8081/request/map/chinaMap/insert', data=city.encode('utf-8'),
                                    headers=headers)
            print(res.text)

    """
        # 写入
        ChinaFile = json.dumps(self.ChinaMap, indent=4, ensure_ascii=False)
        with open('ChinaFile.json', 'w', encoding='utf-8') as json_file:
            json_file.write(ChinaFile)
        print("China success")
        """

    #国外信息
    def abroad_parser(self, abroad_information):
        countries = json.loads(abroad_information.group(0))
        # print(countries)
        for country in countries:
            # print(country['locationId'])
            # 中国没有id,补全
            if country['provinceName']=="中国":
                country["id"]=0

            self.ForeignMap.append({
                "Data": self.date,
                "Country": country['provinceName'],
                "increaseDiagnosis": 0,
                "increaseDeath": 0,
                "increaseCure": 0,
                "increaseSuspected": 0,
                "totalDiagnosis": country['confirmedCount'],
                "totalDeath": country['deadCount'],
                "totalCure": country['curedCount'],
                "totalSuspected": country['suspectedCount'],
                "extanceDiagnosis": country['currentConfirmedCount'],
                "extanceSuspected": 0,
                "id": country['id'],
                "Return":None
            })
        # print(self.ForeignMap)


        #提交
        headers = {
            "content-type": "application/json; charset=UTF-8",
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'
        }
        print("foreign")
        for item in self.ForeignMap:
            # 查询数据
            checkQuery = {
                "Data": item["Data"],
                "Country": item['Country'],
                "Return": 'singleCountry'
            }
            LastQuery = {
                "Data": self.yesterday,
                "Country": item['Country'],
                "Return": 'singleCountry'
            }


            # 每日新增数目
            # Diagnosis
            data = (json.dumps(LastQuery, ensure_ascii=False)).encode('utf-8')
            checkres = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/select',
                                     data=data, headers=headers)
            last = json.loads(checkres.content)
            print(last['result'], last['message'])

            if last['result'] == 'Y' and 'extance' in last['message'].keys() and last['message']['extance']!=None:
                item['increaseDiagnosis']=item['extanceDiagnosis']-last['message']['extance']['confirmedNumber']
            if last['result'] == 'Y' and 'total' in last['message'].keys() and last['message']['total'] != None:
                item['increaseDeath'] = item['totalDeath'] - last['message']['total']['deathToll']
                item['increaseCure'] = item['totalCure'] - last['message']['total']['cureNumber']
            print("increaseDiagnosis:", item['increaseDiagnosis'])
            print("increaseDeath:", item['increaseDeath'])
            print("increaseCure:", item['increaseCure'])

            print(item)

            # 查询数据是否存在
            data = (json.dumps(checkQuery, ensure_ascii=False)).encode('utf-8')
            checkres = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/select',
                                     data=data, headers=headers)
            result = json.loads(checkres.content)

            # total
            item["Return"] = 'total'
            country = json.dumps(item, ensure_ascii=False)
            if result['result'] == 'Y' and 'total' in result['message'].keys() and result['message']['total']!=None:
                # update
                print("update total")
                res = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/update', data=country.encode('utf-8'),
                                    headers=headers)
            else:
                # insert
                print("insert total")
                res = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/insert',
                                    data=country.encode('utf-8'),
                                    headers=headers)
            print(res.text)

            # increase
            item["Return"] = 'newAddtion'
            country = json.dumps(item, ensure_ascii=False)
            if result['result'] == 'Y' and 'newAddtion' in result['message'].keys() and result['message']['newAddtion']!=None:
                # update
                print("update increase")
                res = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/update', data=country.encode('utf-8'),
                                    headers=headers)
            else:
                # insert
                print("insert increase")
                res = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/insert', data=country.encode('utf-8'),
                                    headers=headers)
            print(res.text)

            # exsisting
            item["Return"] = 'extance'
            country = json.dumps(item, ensure_ascii=False)
            if result['result'] == 'Y' and 'extance' in result['message'].keys() and result['message']['extance'] != None:
                # update
                print("update existance")
                res = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/update', data=country.encode('utf-8'),
                                    headers=headers)
            else:
                # insert
                print("insert")
                res = requests.post(url='http://127.0.0.1:8081/request/map/foreignMap/insert',
                                    data=country.encode('utf-8'),
                                    headers=headers)
            print(res.text)

        """
        # 写入
        foreignFile = json.dumps(self.ForeignMap, indent=4, ensure_ascii=False)
        with open('foreignFile.json', 'w', encoding='utf-8') as json_file:
                json_file.write(foreignFile)

        print("Foreign success")
        """

    #提交年龄数据
    def age(self):
        data=[
            {"Age": 0, "totalCure":205,"totalDeath":0},
            {"Age": 10, "totalCure":270, "totalDeath":0},
            {"Age": 20, "totalCure":1374, "totalDeath":0},
            {"Age": 30, "totalCure":2525, "totalDeath":9},
            {"Age": 40, "totalCure":4396, "totalDeath":25},
            {"Age": 50, "totalCure":6834, "totalDeath":83},
            {"Age": 60, "totalCure":6337, "totalDeath":312},
            {"Age": 70, "totalCure":7121, "totalDeath":1090},
            {"Age": 80, "totalCure":5352, "totalDeath":1243},
            {"Age": 90, "totalCure":1115, "totalDeath":285}
        ]
        headers = {
            "content-type": "application/json; charset=UTF-8",
            "user-agent":'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'
        };
        for item in data:
            age = json.dumps(item, ensure_ascii=False)
            print(age)
            # data = age.encode('utf-8')
            # 查询是否存在
            res = requests.post(url='http://127.0.0.1:8081/request/map/Age/select', data={}, headers=headers)
            ageData=json.loads(res.content)
            # 更新/插入
            if ageData['result']=='Y' and ageData['message']!=None:
                res = requests.post(url='http://127.0.0.1:8081/request/map/Age/update', data=age, headers=headers)
            elif ageData['result']=='N' and ageData['message']=='empty':
                res = requests.post(url='http://127.0.0.1:8081/request/map/Age/insert', data=age, headers=headers)
            print(res.text)

    # 提交性别数据
    def sex(self):
        data={"ratioCure":-1,
              "ratioDeath":63.7,
              "ratioConfirmed":51.1
        }   #男性占比
        headers = {
            "content-type": "application/json; charset=UTF-8",
            "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:73.0) Gecko/20100101 Firefox/73.0'
        };
        sex=json.dumps(data,ensure_ascii=False)
        print("sex:")

        # 查询是否存在
        res = requests.post(url='http://127.0.0.1:8081/request/map/Gender/select', data={}, headers=headers)
        sexData = json.loads(res.content)
        # 更新/插入
        if sexData['result'] == 'Y' and sexData['message'] != None:
            res = requests.post(url='http://127.0.0.1:8081/request/map/Gender/update', data=sex, headers=headers)
        elif ageData['result'] == 'N' and ageData['message'] == 'empty':
            res = requests.post(url='http://127.0.0.1:8081/request/map/Gender/insert', data=sex, headers=headers)
        print(res.text)
