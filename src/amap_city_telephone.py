# coding:utf-8

from urllib.parse import urlencode
import requests
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
class aMap(object):
    def __init__(self,ak):
        self.ak=ak
        self.session = requests.Session()

    def Query(self,address,regionid):
        location = None
        res =None
        # if regionid == "":

        query_data = {
            'address': address,
            # 'city': '中国',
            'output': 'json',
            'key': self.ak,
        }

        while True:
            try:
                # http://api.map.baidu.com/geocoder/v2/?address=北京市海淀区上地十街10号&output=json&ak=您的ak&callback=showLocation
                res = self.session.get('https://restapi.amap.com/v3/geocode/geo?' + urlencode(query_data), timeout=10)
                break
            except requests.exceptions.RequestException as e:
                print(e)
                print(self.ak)
                continue

        # {"status":0,"result":{"location":{"lng":116.34272747723579,"lat":40.036034689800448},"precise":1,"confidence":80,"comprehension":97,"level":"UNKNOWN"}}
        if res ==None or res.status_code != 200:
            logging.error(f"send req error! address:{address}")
            if res:
                logging.error(f"{res},code:{res.status_code}")
            return (False,location)
        try:
            location_json = res.json()
        except:
            logging.error("{}解析错误".format(res))
        else:

            if location_json['status'] == "1" and location_json['geocodes']:
                # print(location_json)
                # print(i, com_tuple, location_json)
                for geocode in location_json['geocodes']:

                    location = geocode['location']
                    adcode = geocode['adcode']
                    if adcode.__len__()==6:
                        regionid =  adcode
                    return (True, location,regionid)
            else:
                return (True, location, regionid)

        return (False ,location,regionid)
    def QuerycompanyAddress(self,companyname,address,regionid):
        res,location,regionid = self.Query(address,regionid)
        if res:
            return companyname,location,regionid
        return None,None,None
    def query_keyword(self,keyword):
        location = None
        res = None
        area_code = ""
        location = ""
        tel_lenth = 0
        address = ""
        # if regionid == "":

        query_data = {
            'keywords': keyword,
             "city":keyword,
            'types': '政府机构及社会团体',
            'output': 'json',
            'children':'1',
            'key': self.ak,
        }

        while True:
            try:
                # http://api.map.baidu.com/geocoder/v2/?address=北京市海淀区上地十街10号&output=json&ak=您的ak&callback=showLocation
                # restapi.amap.com/v3/place/text?key=您的key&keywords=苏州市&types=政府&city=苏州市&children=1&offset=20&page=1&extensions=all
                res = self.session.get('http://restapi.amap.com/v3/place/text??' + urlencode(query_data), timeout=10)
                break
            except requests.exceptions.RequestException as e:
                print(e)
                print(self.ak)
                continue

        # {"status":0,"result":{"location":{"lng":116.34272747723579,"lat":40.036034689800448},"precise":1,"confidence":80,"comprehension":97,"level":"UNKNOWN"}}
        if res == None or res.status_code != 200:
            logging.error(f"send req error! address:{keyword}")
            if res:
                logging.error(f"{res},code:{res.status_code}")
            return (False, location)
        try:
            location_json = res.json()
        except:
            logging.error("{}解析错误".format(res))
        else:

            if location_json['status'] == "1" and location_json['pois']:
                # print(location_json)
                # print(i, com_tuple, location_json)
                for _pois in location_json['pois']:

                    if "name" in _pois:
                        name = _pois['name']
                        if "人民政府" in name and location == "":
                            if "location" in _pois:
                                location = _pois['location']
                            if "address" in _pois:
                                address = _pois['address']
                    tel = _pois['tel']
                    # 判断是string还是array
                    # print(tel)

                    if not isinstance(tel,list):
                        _tel=tel.split(";")
                        for _i in _tel:
                            split_i = _i.split("-")
                            area_code_tmp = split_i[0]
                            if tel_lenth <7 or tel_lenth > 8:
                                tel_lenth = split_i[1].__len__()
                                area_code = area_code_tmp
                    if tel_lenth >=7 and tel_lenth<=8 and (not location=="") and (not address =="") and area_code.__len__() > 2:
                        break
        return tel_lenth,area_code,location,address


if __name__ == "__main__":
    amap = aMap("876104e434b73c9e020b57a1e61474ca")
    with open("../data/city_data.csv","w",encoding="utf-8") as outp:
        with open("/home/michael/Downloads/BaiduMap_cityCode_1102.txt","r" ,encoding="utf-8") as inp:
            for content in inp:
                city = content.strip("\r\n").split(",")[-1]
                tel_lenth,area_code,location,address = amap.query_keyword(city)
                outp.write("{},{},{},{},{}\n".format(city,tel_lenth,area_code,location,address))
