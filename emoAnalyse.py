from flask import Flask, request, render_template
from flask import jsonify
import pandas as pd
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json,traceback,os.path
from pandas import ExcelWriter
from pandas import ExcelFile
from flask_ngrok import run_with_ngrok
import dialogflow
import sys
import requests

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from nltk.tokenize import word_tokenize  # to split sentences into words
from nltk.corpus import stopwords  # to get a list of stopwords
from collections import Counter  # to get words-frequency
import requests  # this we will use to call API and get data
import json  # to convert python dictionary to string format
import nltk

nltk.download('stopwords')

from helper import dbHandler


app = Flask(__name__)

#run_with_ngrok(app)
NEWS_API_KEY = "02045abef4484928879964f30d14957a"

# cross origin

CORS(app, resources={r"*": {"origins": "*"}})



@app.route('/')
def index():

        return render_template('pages/login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        df = pd.read_csv(request.files.get('file'),encoding = "utf-8")
        df_json = json.loads(df.to_json(orient='records'))
        response = dbHandler.insertData(df_json)
        print ("response",response)
        message = response["msg"]
        return render_template('pages/upload.html', message=message)
    return render_template('pages/upload.html')
    
@app.route('/viewSentiment', methods=['GET', 'POST'])
def viewSentiment():
    return render_template('pages/displaySentiment.html')

    
@app.route('/displaySentiment', methods=['GET', 'POST'])
def displaySentiment():
        
        sen_wordCloud = dbHandler.getSentiment()
        print(sen_wordCloud)
        # url = "https://newsapi.org/v1/articles?source=bbc-news&apiKey="+NEWS_API_KEY

        # # call the api
        # response = requests.get(url)
        # #print("response",response)

        # # get the data in json format
        # result = response.json()
        # print("result",result)
        # # all the news articles are listed under 'articles' key
        # # we are interested in the description of each news article
        # sentences = ""
        # for news in result['articles']:
            # description = news['description']
            # sentences = sentences + " " + description
        # print("sentences",sentences)

        # # split sentences into words
        # words = word_tokenize(sentences)
        # #print("words",words)
        # # get stopwords
        # stop_words = set(stopwords.words('english'))

        # # remove stopwords from our words list and also remove any word whose length is less than 3
        # # stopwords are commonly occuring words like is, am, are, they, some, etc.
        # words = [word for word in words if word not in stop_words and len(word) > 3]

        # # now, get the words and their frequency
        # words_freq = Counter(words)

        # # JQCloud requires words in format {'text': 'sample', 'weight': '100'}
        # # so, lets convert out word_freq in the respective format
        # words_json = [{'text': word, 'weight': count} for word, count in words_freq.items()]
        #print("words_json",words_json)
        # now convert it into a string format and return it
        return json.dumps(sen_wordCloud)
        
        
@app.route('/displayPositive', methods=['GET', 'POST'])
def displayPositive():
        
        pos_wordCloud = dbHandler.getPositive()
        
        print("emo analyse")
        return json.dumps(pos_wordCloud)
        
@app.route('/displayNegative', methods=['GET', 'POST'])
def displayNegative():
        
        neg_wordCloud = dbHandler.getNegative()
        
        print("emo analyse")
        return json.dumps(neg_wordCloud)
        
@app.route('/sentimentDistribution', methods=['GET', 'POST'])
def sentimentDistribution():
        
        response = dbHandler.sentimentDistribution()
        print(response)
        return json.dumps(response)
    
@app.route('/authenticate/<authType>', methods=['POST'])
def authenticate(authType):
    try:
        if authType == "login":
            print("******")
            username = request.form['user_id']
            password = request.form['password']
            response = dbHandler.loginCheck(username,password)
        elif authType == "train":
            print("******")
            response = dbHandler.trainModel()
        elif authType == "logout":
            response={
                "status":True,
                "msg":"Logged out succesfully"
            }

    except Exception as e:
        print(e)
        response = {
            "status":False,
            "msg":"[error] occured while authenticating user"
        }
    print ("response",response)
    return jsonify(response=response)


    
    

if __name__ == '__main__':
    app.run()