import requests
from bs4 import BeautifulSoup
import bs4.element
from datetime import datetime
import time
import numpy
import schedule


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nikearlam-default-rtdb.firebaseio.com/'
})
fireKeyList = []
# BeautifulSoup 객체 생성
def get_soup_obj(url):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; ; NCLIENT50_AAPDC42CAF9285) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.text,'lxml')
    return soup

def isExist(list , key):#등록하려는 배열에 중복제거
    isOverlap = False
    for data in list:
        if(data.productKey == key):
            isOverlap = True
            break
        
    return isOverlap

def isFireExist(key):#파이어 베이스 DB안에 중복되는 데이터 있을 경우 제외
    if(fireKeyList.index(key) > -1):
        return True
    else:
        return False

def getProductInfo(productList): 
    nikeList = []
    for a in productList:
        productUrl = a.attrs.get('href')
        productName = a.attrs.get('title')
        productKey = a.attrs.get('data-tag-pw-rank-product-id')
        monthStr = ''
        dayStr = ''
        imageSrc = ''
        
        if None != a.find('p','headline-4') : monthStr = a.find('p','headline-4').text
        if None != a.find('p','headline-1') : dayStr = a.find('p','headline-1').text
        if None != a.find('img') : imageSrc = a.find('img').attrs.get('data-src')

        if(monthStr != '') :
            if(isExist(nikeList,productKey) == False):
                if(isFireExist(productKey) == False):
                    nikeData = {
                        "productKey" : productKey
                        , "productUrl" : productUrl
                        , "productName": productName
                        , "monthStr"   : monthStr
                        , "dayStr"     : dayStr
                        , "imageSrc"   : imageSrc
                    }
                    nikeList.append(nikeData)
    return nikeList


def saveNike(nikeList):
    for nike in nikeList:
        productKey = nike['productKey'] 
        month = nike['month']
        
        imageSrc = nike['imageSrc']
        pathStr = '/nike/'+productKey
        ref = db.reference(pathStr)
        ref.set(nike)


# 나이키 목록 가져오기
def getNikeData():
    connectUrl = "https://www.nike.com/kr/launch/?type=upcoming"
    soup = get_soup_obj(connectUrl)
    productList = soup.find('ul', 'item-list-wrap').find_all('li', 'launch-list-item')
    productName = getDetailInfo(productList)
    return productName

def getDetailInfo(productList):
    nikeList = []
    for product in productList:

        productKey   = product.find('a', 'card-link').attrs.get('data-tag-pw-rank-product-id')
        productName  = product.find('a', 'card-link').attrs.get('title')
        productUrl   = 'https://www.nike.com' + product.find('a', 'card-link').attrs.get('href')
        imageSrc     = product.find('img', 'img-component').attrs.get('data-src')
        eventDate = product.attrs.get('data-active-date')+ ":00"
        dateStr = eventDate.split(' ')[0].replace('/','')
        timeStr = eventDate.split(' ')[1]
        yyyy = eventDate.split(' ')[0].split('/')[0]
        mm = eventDate.split(' ')[0].split('/')[1]
        dd = eventDate.split(' ')[0].split('/')[2]
        eventDateText = ''
        if(product.find('div','available-date-component') != None):
            eventDateText = product.find('div','available-date-component').text
        if(eventDateText != ''):
            nikeData = {
                    "productKey" : productKey
                    , "productUrl" : productUrl
                    , "productName": productName
                    , "imageSrc"   : imageSrc
                    , "dateStr" : dateStr
                    , "time" : timeStr
                    , "year"   : yyyy
                    , "month"   : mm
                    , "day"     : dd
                    , "eventDate"     : eventDate
                    , "eventDateText"     : eventDateText
                }
            nikeList.append(nikeData)
    return nikeList

def getFireNikeData():
    ref = db.reference('nike')
    snapshot = ref.get()
    if(snapshot != None):
        for key, val in snapshot.items():
            fireKeyList.append(key)

def callNikeData():
    nikeData = getNikeData()
    saveNike(nikeData)

def job():
    print("호출")
    getFireNikeData()
    callNikeData()

if __name__ == "__main__":
    job()
    #schedule.every().day.at("23:21").do(job)
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)

