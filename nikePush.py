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



nikeList = []
toDayPushData = []#금일 푸쉬 대기 데이터
searchDate = ''

# 나이키 목록 가져오기
def getFireNikeData():
    ref = db.reference('nike')
    snapshot = ref.get()
    if(snapshot != None):
        for key, val in snapshot.items():
            nikeList.append(val)
    print(len(nikeList))

def getTodayData():#금일 푸쉬 대기 데이터 추출
        nowDate = datetime.today().strftime("%Y%m%d")
        for nike in nikeList:
                if(nike['dateStr']  == nowDate):
                        toDayPushData.append(nike)
        print(len(toDayPushData))

def checkPushData():#금일 푸쉬될 데이터 시간에 맞춰서 푸쉬하기
        checkTime = datetime.today().strftime("%H:%M") + ":00"
        pushList = []
        for nike in toDayPushData:
                if(nike['time']  == checkTime):
                        pushList.append(nike)
        saveNike(pushList)
        idexs = []
        for nike in pushList:
                for i in range(len(toDayPushData)):
                        delData = toDayPushData[i]
                        if(nike['productKey'] == delData['productKey']):
                                idexs.append(i)
        numpy.delete(toDayPushData, idexs)


def saveNike(saveNikeList):# 푸쉬
    for nike in saveNikeList:
        productKey = nike['productKey'] 
        month = nike['month']
        
        imageSrc = nike['imageSrc']
        pathStr = '/push/'+productKey
        ref = db.reference(pathStr)
        ref.set(nike)

def delPush():# 푸쉬
        pathStr = '/push/'
        ref = db.reference(pathStr)
        ref.set({})

def clearData():#푸쉬 데이터 삭제
        nikeList = []
        toDayPushData = []    
        delPush()

def pushChk():
        if(len(toDayPushData)>0):#금일 푸쉬 목록에 데이터가 있으면 계속 호출
                checkPushData()


def delExpDateAfter():
        for nike in nikeList:
                nowDate = datetime.today().strftime("%Y%m%d")
                if(nike['dateStr']  < nowDate):
                        key = nike['productKey']
                        db.reference('nike/'+key).delete()
               

 if __name__ == "__main__":
        schedule.every().day.at("08:00").do(getFireNikeData)#매일 아침 8시 나이키 데이터 조회
        schedule.every().day.at("09:00").do(getTodayData)#매일 아침 8시 나이키 데이터 조회
        schedule.every().day.at("00:00").do(clearData)#매일 12시에 데이터 초기화
        schedule.every().day.at("13:00").do(delExpDateAfter)#매일 1시에 어제 날짜 데이터는 삭제
        schedule.every(3).seconds.do(pushChk) # 3초마다 job 실행
        while False:                 
                schedule.run_pending()
                time.sleep(1)