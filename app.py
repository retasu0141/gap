# インストールしたパッケージのインポート
from flask import Flask, render_template, request, redirect, url_for, make_response
from pytrends.request import TrendReq  #グーグルトレンドの情報取得
import pandas as pd  #データフレームで扱う
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import datetime
import codecs
from datetime import date, datetime, timedelta
from io import BytesIO
import urllib
import os

# appという名前でFlaskのインスタンスを作成
PEOPLE_FOLDER = os.path.join('static', 'photo')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER
data = {
    'keyword': ''
}

@app.route('/')
def main():
    return render_template('form.html')

@app.route('/post', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form['name']
        # 今日
        today = date.today()

        # 30日前
        day = today - timedelta(30)

        #print(day)

        dt_now = datetime.now()

        dt_now_s = str(dt_now.microsecond)
        pytrends = TrendReq(hl='ja-JP', tz=360)
        #keyword=''
        kw_list = [keyword]
        pytrends.build_payload(kw_list, cat=0, timeframe=str(day)+' '+str(today), geo='JP', gprop='')
        df = pytrends.interest_over_time() #時系列データを取り出す
        df.to_csv(dt_now_s+".csv", encoding='cp932')
        #関連トピック
        df = pytrends.related_topics()
        #トップ
        try:
            text_ = df[keyword]['top'].loc[:,['topic_title']].head(10)
            text__ = text_['topic_title']
            _text = '\n・'.join(text__)
            text = _text.replace('Name: topic_title, dtype: object', '')
        except:
            text = 'なし'
        #上昇
        try:
            text2_ = df[keyword]['rising'].loc[:,['topic_title']].head(10)
            text2__ = text2_['topic_title']
            _text2 = '\n・'.join(text2__)
            text2 = _text2.replace('Name: topic_title, dtype: object', '')
        except:
            text2 = 'なし'


        #関連キーワード
        df = pytrends.related_queries()
        #トップ
        try:
            text3_ = df[keyword]['top'].head(10)
            text3__ = text3_['query']
            _text3 = '\n・'.join(text3__)
            text3 = _text3.replace('Name: query, dtype: object', '')
        except:
            text3 = 'なし'
        #上昇
        try:
            text4_ = df[keyword]['rising'].head(10)
            text4__ = text4_['query']
            _text4 = '\n・'.join(text4__)
            text4 = _text4.replace('Name: query, dtype: object', '')
        except:
            text4 = 'なし'

        #print(keyword+'.csv')

        df = pd.read_csv(dt_now_s+'.csv',encoding='cp932')


        '''
        print(df)
        print(df.columns)
        print(df['date'])
        print(df[keyword])
        '''

        #グラフの作成
        fig = plt.figure()
        plt.figure(1)
        plt.plot(df['date'],df[keyword],marker="o")
        #グラフの軸
        plt.xlabel(df['date'].name)
        plt.ylabel(keyword)

        fig.savefig("static\photo\img.png")
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'img.png')


        #グラフ表示
        #plt.show()
        return render_template('choice.html',text=text,text2=text2,text3=text3,text4=text4,img=full_filename)

if __name__ == '__main__':
    # 作成したappを起動
    # ここでflaskの起動が始まる
    app.run()