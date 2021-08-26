import requests
from bs4 import BeautifulSoup
import bs4.element
import datetime
import time
import numpy

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://nikearlam-default-rtdb.firebaseio.com/'
})

# BeautifulSoup 객체 생성
def get_soup_obj(url):
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; ; NCLIENT50_AAPDC42CAF9285) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36'}
    res = requests.get(url, headers = headers)
    soup = BeautifulSoup(res.text,'lxml')
    return soup

def isExist(list , key):
    isOverlap = False
    for data in list:
        if(data.productKey == key):
            isOverlap = True
            break
        
    return isOverlap

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
            if(isExist(nikeData,productKey)):
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
        year = nike['year'] 
        month = nike['month']
        
        imageSrc = nike['imageSrc']
        pathStr = '/nike/'+year+month
        ref = db.reference(pathStr)
        ref.push(nike)


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
        eventDate = product.attrs.get('data-active-date')
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

        

def callNikeData(monthList):
    nikeData = getNikeData()
    saveNike(nikeData)

if __name__ == "__main__":
    
    monthList = [8,9,10]
    callNikeData(monthList)