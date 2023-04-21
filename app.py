from flask import Flask, render_template, request,send_file
import spacy
import pandas as pd
import tweepy
from textblob import TextBlob
import string


consumer_key = "10yh2JisP7UC1yrJZc124IYqH"
consumer_secret =  "WIwZeogjvWJe0vQLfaNRQ2eosfwZgiE53rE8IREabFpOzMPMKS"
access_key ="1437038540391649284-mrXjVY9Xw92V5TsymunFkiiIzV1iXg"
access_secret = "wynX8FjopgU33joYxedQXhErvhmdQaEZMyMkqIZyrpPm4"


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

def remove_punctuation(tweet):

    return ''.join(ch for ch in tweet if ch not in set(string.punctuation))

def remove_sw(tweet):

    sp=spacy.load('en_core_web_sm')
    sw=sp.Defaults.stop_words
    tweet=tweet.lower()
    tweet = ' '.join([w for w in tweet.split(' ') if w not in sw])
    return tweet


def tweet_sentiment(tweet):
    tb = TextBlob(tweet)
    score = tb.sentiment.polarity
    if score > 0:
        return 'Positive'
    
    elif score <0:
        return 'Negative'
    else:
        return 'Neutral'

    
db = pd.DataFrame(columns=['username','text',])

def scrape(words, date_since, numtweet):

    tweets = api.search_tweets(words, lang="en",
                        since_id=date_since,
                        tweet_mode='extended',count=numtweet)

    list_tweets = [tweet for tweet in tweets]

    for tweet in list_tweets:
        username = tweet.user.screen_name
        hashtags = tweet.entities['hashtags']
        try:
            text = tweet.retweeted_status.full_text
        except AttributeError:
            text = tweet.full_text
        hashtext = list()
        for j in range(0, len(hashtags)):
            hashtext.append(hashtags[j]['text'])

        ith_tweet = [username, text]
        db.loc[len(db)] = ith_tweet
        


    db['clean']=db['text'].apply(remove_punctuation)
    db['stop_word']=db['clean'].apply(remove_sw)
    db['sentiment'] = db['stop_word'].apply(tweet_sentiment)
    db.drop(['clean','stop_word'],axis=1, inplace=True)



		
app = Flask(__name__)

@app.route('/')
def home():
	return render_template('home.html')


@app.route('/predict',methods=['POST'])
def predict():

    if request.method == 'POST':
        hashtag = request.form['hashtag']
        date=request.form['date']
        tweets=request.form['tweets']
        
        
        scrape(hashtag, date, tweets)
        db.to_csv('Pred.csv',index=False)
        return send_file('Pred.csv',as_attachment=True)
    
    return render_template('home.html')

if __name__ == '__main__':
	app.run(debug=True)



