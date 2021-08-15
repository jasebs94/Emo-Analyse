from pymongo import MongoClient
from datetime import datetime,timedelta
from pyshorteners import Shortener 
import json
import requests
import pandas as pd
import gridfs
from sseclient import SSEClient
from transformers import pipeline

from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

from nltk.tokenize import word_tokenize  # to split sentences into words
from nltk.corpus import stopwords  # to get a list of stopwords
from collections import Counter  # to get words-frequency
import requests  # this we will use to call API and get data
import nltk




#Function to initiate database connection
def getDbConnection():
    try:
        
        print("getDbConnection")
        client = MongoClient('mongodb://localhost:27017/pythonProject')
        print("[INFO] Database connection successful")
        return {'success':True, 'connection':client}
    except Exception as ex:
        print("[ERROR] Database connection failed",exc_info=True)
        return {'success':False}


 
def loginCheck(userid,password):
    print("[info] in login check")
    try:
        print("try")
        dbConfig =  getDbConnection()
        if dbConfig['success']==True:
            client = dbConfig['connection']
            mydb=client['pythonProject']
            userCollection=mydb['users']
            userRecords=userCollection.find({"userid":userid,"password":password})
            if(userRecords.count()==0):
                print("[INFO] Invalid username or password. Unsuccesful login attempt .")
                response={'status': False, "msg":"Please provide correct user credentials to continue"}
            else:
                print("[INFO] login check success")
                response = {'status': True, "msg":"Successfully, Logged In"}
            dbConfig['connection'].close()
            
        else:
            print("[error] unable to connect to database")
            response = {'status': False, "msg":"We are unable to connect to our database. Please try after sometime"}

    except Exception as ex:
        print("[error] Error Occured in login check")
        print(ex)
        response = {
            "status":False,
            "msg":"[error] occured while authenticating user"
        }
    return response

def insertData(df_json):
    print("[info] in insertData")
    try:
        dbConfig =  getDbConnection()
        if dbConfig['success']==True:
            client = dbConfig['connection']
            mydb=client['pythonProject']
            excelDataCollection=mydb['excelData']
            excelDataCollection.insert(df_json)
            dbConfig['connection'].close()
            response = {'status': True, "msg":"Successfully inserted data"}
            
        else:
            print("[error] unable to connect to database")
            response = {'status': False, "msg":"We are unable to connect to our database. Please try after sometime"}

    except Exception as ex:
        print("[error] Error Occured in insertData")
        print(ex)
        response = {
            "status":False,
            "msg":"[error] occured while inserting data"
        }
    return response
    
def trainModel():
    print("[info] in trainModel")
    try:
        print("try")
        nlp = pipeline("sentiment-analysis")
        dbConfig =  getDbConnection()
        if dbConfig['success']==True:
            client = dbConfig['connection']
            mydb=client['pythonProject']
            excelDataCollection=mydb['excelData']
            trainRecords=excelDataCollection.find()
            trainList=[]
            for i in range(0,trainRecords.count()):
                trainList.append(trainRecords[i]['Review'])
            traindf = pd.DataFrame(trainList)
                
            if(trainRecords.count()==0):
                print("[INFO] No Data present .")
                response={'status': False, "msg":"No data available to train"}
            else:
                print("[INFO] trainModel success")
                trainRecords.close()
                print(traindf)
                sentiment = []
                for j in trainList:
                    #sentiment.append(nlp(j))
                    sentimentDict={"Review":j,"Sentiment":nlp(j)}
                    sentiment.append(sentimentDict)
                print(sentiment)
                for sentiments in sentiment:
                    print(sentiments['Sentiment'][0]['label'])
                    sentimentDataCollection=mydb['sentimentData']
                    sentimentdatacollectionDict={"review":sentiments['Review'],"sentiment":sentiments['Sentiment'][0]['label']}
                    x=sentimentDataCollection.insert_one(sentimentdatacollectionDict)
                print(x.inserted_id)
                response = {'status': True, "msg":"Successfully trained"}
            dbConfig['connection'].close()
            
        else:
            print("[error] unable to connect to database")
            response = {'status': False, "msg":"We are unable to connect to our database. Please try after sometime"}

    except Exception as ex:
        print("[error] Error Occured in trainModel")
        print(ex)
        response = {
            "status":False,
            "msg":"[error] occured while trainModel"
        }
    return response
    
    
    
def getSentiment():
    print("[info] in getSentiment")
    try:
        dbConfig =  getDbConnection()
        if dbConfig['success']==True:
            client = dbConfig['connection']
            mydb=client['pythonProject']
            sentimentDataCollection=mydb['sentimentData']
            sentimentDataRecords=sentimentDataCollection.find()
            sentimentDataList=[]
                
            if(sentimentDataRecords.count()==0):
                print("[INFO] No Data present .")
                response={'status': False, "msg":"No data available "}
            else:
                print("[INFO] getSentiment success")

                for i in range(0,sentimentDataRecords.count()):

                    sentimentDict={"Review":sentimentDataRecords[i]['review'],"Sentiment":sentimentDataRecords[i]['sentiment']}
                    sentimentDataList.append(sentimentDict)
                #print(sentimentDataList)
                sentimentDataRecords.close()

                result = json.dumps(sentimentDataList)

                #print(sentimentDataList[0])
                sentences = ""
                for news in sentimentDataList:
                    description = news['Review']
                    sentences = sentences + " " + description
  
                words = word_tokenize(sentences)
   
                stop_words = set(stopwords.words('english'))

                words = [word for word in words if word not in stop_words and len(word) > 3]

       
                words_freq = Counter(words)

                words_json = [{'text': word, 'weight': count} for word, count in words_freq.items()]
          
            
            dbConfig['connection'].close()
            response = words_json
            
        else:
            print("[error] unable to connect to database")
            response = {'status': False, "msg":"We are unable to connect to our database. Please try after sometime"}

    except Exception as ex:
        print("[error] Error Occured in getSentiment")
        print(ex)
        response = {
            "status":False,
            "msg":"[error] occured while getSentiment"
        }
    return response
    
    
def getPositive():
    print("[info] in getPositive")
    try:
        dbConfig =  getDbConnection()
        if dbConfig['success']==True:
            client = dbConfig['connection']
            mydb=client['pythonProject']
            sentimentDataCollection=mydb['sentimentData']
            sentimentDataRecords=sentimentDataCollection.find()
            sentimentDataList=[]
                
            if(sentimentDataRecords.count()==0):
                print("[INFO] No Data present .")
                response={'status': False, "msg":"No data available "}
            else:
                print("[INFO] getPositive success")

                for i in range(0,sentimentDataRecords.count()):

                    sentimentDict={"Review":sentimentDataRecords[i]['review'],"Sentiment":sentimentDataRecords[i]['sentiment']}
                    sentimentDataList.append(sentimentDict)
                print("1")
                print(sentimentDataList)
                sentimentDataRecords.close()

                result = json.dumps(sentimentDataList)
                print("2")
                print(sentimentDataList[0])
                sentences = ""
                for word in sentimentDataList:
                    print(word['Sentiment'])
                    if word['Sentiment'] == "POSITIVE":  
                        description = word['Review']
                        sentences = sentences + " " + description
  
                words = word_tokenize(sentences)
   
                stop_words = set(stopwords.words('english'))

                words = [word for word in words if word not in stop_words and len(word) > 3]

       
                words_freq = Counter(words)

                words_json = [{'text': word, 'weight': count} for word, count in words_freq.items()]
          
            
            dbConfig['connection'].close()
            response = words_json
            
        else:
            print("[error] unable to connect to database")
            response = {'status': False, "msg":"We are unable to connect to our database. Please try after sometime"}

    except Exception as ex:
        print("[error] Error Occured in getPositive")
        print(ex)
        response = {
            "status":False,
            "msg":"[error] occured while getPositive"
        }
    return response
    

    

def getNegative():
    print("[info] in getNegative")
    try:
        dbConfig =  getDbConnection()
        if dbConfig['success']==True:
            client = dbConfig['connection']
            mydb=client['pythonProject']
            sentimentDataCollection=mydb['sentimentData']
            sentimentDataRecords=sentimentDataCollection.find()
            sentimentDataList=[]
                
            if(sentimentDataRecords.count()==0):
                print("[INFO] No Data present .")
                response={'status': False, "msg":"No data available "}
            else:
                print("[INFO] getNegative success")

                for i in range(0,sentimentDataRecords.count()):

                    sentimentDict={"Review":sentimentDataRecords[i]['review'],"Sentiment":sentimentDataRecords[i]['sentiment']}
                    sentimentDataList.append(sentimentDict)
                print("1")
                print(sentimentDataList)
                sentimentDataRecords.close()

                result = json.dumps(sentimentDataList)
                print("2")
                print(sentimentDataList[0])
                sentences = ""
                for wordn in sentimentDataList:
                    print(wordn['Sentiment'])
                    if wordn['Sentiment'] == "NEGATIVE":  
                        description = wordn['Review']
                        sentences = sentences + " " + description
  
                words = word_tokenize(sentences)
   
                stop_words = set(stopwords.words('english'))

                words = [word for word in words if word not in stop_words and len(word) > 3]

       
                words_freq = Counter(words)

                words_json = [{'text': word, 'weight': count} for word, count in words_freq.items()]
          
            
            dbConfig['connection'].close()
            response = words_json
            
        else:
            print("[error] unable to connect to database")
            response = {'status': False, "msg":"We are unable to connect to our database. Please try after sometime"}

    except Exception as ex:
        print("[error] Error Occured in getNegative")
        print(ex)
        response = {
            "status":False,
            "msg":"[error] occured while getNegative"
        }
    return response




def sentimentDistribution():
    print("[info] in sentimentDistribution")
    try:
        dbConfig =  getDbConnection()
        if dbConfig['success']==True:
            client = dbConfig['connection']
            mydb=client['pythonProject']
            sentimentDataCollection=mydb['sentimentData']
            sentimentDataRecords=sentimentDataCollection.find()
            sentimentDataList=[]
                
            if(sentimentDataRecords.count()==0):
                print("[INFO] No Data present .")
                response={'status': False, "msg":"No data available "}
            else:
                print("[INFO] sentimentDistribution success")

                for i in range(0,sentimentDataRecords.count()):

                    sentimentDict={"Review":sentimentDataRecords[i]['review'],"Sentiment":sentimentDataRecords[i]['sentiment']}
                    sentimentDataList.append(sentimentDict)
                print(sentimentDataList)
                sentimentDataRecords.close()
                pos = 0
                neg = 0
                for sentiment in sentimentDataList:
                    if sentiment['Sentiment'] == "NEGATIVE":
                        neg = neg+1                  
                    elif sentiment['Sentiment'] == "POSITIVE":
                        pos = pos+1
                response = {"POSITIVE":pos,"NEGATIVE":neg}    
          
            
            dbConfig['connection'].close()
            response = response
            
        else:
            print("[error] unable to connect to database")
            response = {'status': False, "msg":"We are unable to connect to our database. Please try after sometime"}

    except Exception as ex:
        print("[error] Error Occured in sentimentDistribution")
        print(ex)
        response = {
            "status":False,
            "msg":"[error] occured while sentimentDistribution"
        }
    return response
    
    
    
  