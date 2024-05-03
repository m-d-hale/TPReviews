#IMPORT PACKAGES
####################################################################################################

import pandas as pd
import numpy as np
import pathlib
import itertools
from rake_nltk import Rake

import json
import requests
from urllib.parse import urlparse

import re
from datetime import datetime

from tabulate import tabulate

import matplotlib.pyplot as plt
import seaborn as sns

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('vader_lexicon')

#IMPORT AND PROCESS JSON PRODUCED BY SCRAPY SPIDER
####################################################################################################

#Read in, process and print the JSON table (NB: add a category for non invited/verified reviews)
#Convert to datetime
df_trustpilot = pd.read_json('TrustPilot.json')
df_trustpilot['Experience_Date'] = pd.to_datetime(df_trustpilot['Experience_Date'])
df_trustpilot['Posted_DateTime'] = pd.to_datetime(df_trustpilot['Posted_DateTime'])

#Create organisation field from URL
#ptrn1 = r"https://uk.trustpilot.com/review/"
#ptrn2 = r"\Auk."
#ptrn3 = r'[?]page=' 
#ptrn4 = r'\Awww.'
#ptrn5 = r'[^A-Za-z.]+' 
#ptrn6 = r'\..*$'

#df_trustpilot['Bank'] = df_trustpilot['url'].str.replace(ptrn1,'')
#df_trustpilot['Bank'] = df_trustpilot['Bank'].str.replace(ptrn2,'')
#df_trustpilot['Bank'] = df_trustpilot['Bank'].str.replace(ptrn3,'')
#df_trustpilot['Bank'] = df_trustpilot['Bank'].str.replace(ptrn4,'')
#df_trustpilot['Bank'] = df_trustpilot['Bank'].str.replace(ptrn5,'')
#df_trustpilot['Bank'] = df_trustpilot['Bank'].str.replace(ptrn6,'')

#Extract the organisation name from the url
df_trustpilot['Brand'] = df_trustpilot['url'].str.extract(r'review/(?:www\.)?(.*?)\.')

#Change none to space for reviews, so ablt to still pull title in concatenated title/review field
def ystr(x):
    return '' if x is None else str(x)
df_trustpilot['Review_Text'] = df_trustpilot['Review_Text'].apply(lambda row: ystr(row))

df_trustpilot['Review_TitleAndText'] = df_trustpilot['Review_Title'] + ' : ' + df_trustpilot['Review_Text']
df_trustpilot['ReviewNum'] = np.arange(len(df_trustpilot)) + 1

#Call those that didn't have verified/invited on the review (i.e. unsolicited reviews)
def xstr(x):
    return 'Unsolicited' if x is None else str(x)
df_trustpilot['Review_Type'] = df_trustpilot['Review_Type'].apply(lambda row: xstr(row))

#Extract keywords from reviews into a column
rk = Rake()
def key(x):
    rk.extract_keywords_from_text(x)
    return rk.get_ranked_phrases()[:5]
df_trustpilot['KeyPhrases'] = df_trustpilot['Review_TitleAndText'].apply(lambda row: key(row))
df_trustpilot['KeyPhrases'] = df_trustpilot['KeyPhrases'].str.get(0)





#INITIAL ANALYSIS: ADD LABELS FOR EACH WORD
####################################################################################################

#Get variable names
print(df_trustpilot.columns)

#Take a look at the text of the reviews
print(df_trustpilot['Review_Title'].head())
print(df_trustpilot['Review_Text'].head())

#Count Breakdowns
star_counts = df_trustpilot['Review_Stars'].value_counts().sort_values(ascending=False)
print(star_counts)

num_review_counts = df_trustpilot['Num_Of_Reviews'].value_counts().sort_values(ascending=False)
print(num_review_counts)

reviewtype_counts = df_trustpilot['Review_Type'].value_counts().sort_values(ascending=False)
print(reviewtype_counts)

#Visualise when reviews were done during the day
sns.set_theme()
df_trustpilot['hour'] = df_trustpilot['Posted_DateTime'].dt.hour
hourly_counts = df_trustpilot.groupby(['Review_Type','hour']).size().reset_index(name='count')
hourly_counts['percent'] = hourly_counts.groupby(['Review_Type'])['count'].transform(lambda x: x / x.sum())
plt.figure(figsize=(10,6))
sns.lineplot(data=hourly_counts, x='hour', y='percent', hue='Review_Type')
plt.xlabel('Hour of day')
plt.ylabel('% of reviews')
plt.savefig('timeofday.png')
plt.show()


#Most common words in reviews
####################################################################################################

#Define a pattern (rege) to extract words and remove symbols
pattern = r"([^A-Za-z\d#@]|'(?![A-Za-z\d#@]))"

#Clean the text, extract words for all reviews, remove blanks and stopwords like and/or etc
df_trustpilot_alt = df_trustpilot.assign(words = df_trustpilot['Review_Text'].str.lower().str.split())

review_words = df_trustpilot_alt.explode('words')
review_words['words'] = review_words['words'].str.replace(pattern, '')
review_words = review_words[~review_words['words'].isin(stopwords.words('english'))]
review_words = review_words[~review_words['words'].isin([' ','',None])]

#Most commonly used words
word_counts = review_words['words'].value_counts().sort_values(ascending=False)
type(word_counts)
print(word_counts[:20])

#Sentiment Analysis Word by Word
####################################################################################################

#Sentiment analysis word by word (NB: trad way, using lexicons)

#Create sentiment intensity analyser object
sia = SentimentIntensityAnalyzer()

#Apply sentiment analysis to each review word
review_words['sentiment'] = review_words['words'].apply(lambda word: sia.polarity_scores(str(word))['compound'])
review_words_grpbystars = review_words.groupby('Review_Stars')['sentiment'].mean().reset_index()
review_words_grpbyreview = review_words.groupby('ReviewNum')['sentiment'].mean().reset_index()

#Print Sentiment Analysis Results
print(review_words_grpbystars)
print(review_words_grpbyreview)

#Sentiment Analysis by Review
####################################################################################################

#Sentiment analysis on each review (Vader can do this)

#Create function to apply sentiment score (to not throw errors when review text is empty)
def CalcSentim(x):
    try:
        return sia.polarity_scores(str(x))['compound']
    except:
        return np.nan

df_trustpilot['TitleAndReview_Sentiment'] = df_trustpilot['Review_TitleAndText'].apply(CalcSentim)
df_trustpilot['Review_Sentiment'] = df_trustpilot['Review_Text'].apply(CalcSentim)
df_trustpilot['Title_Sentiment'] = df_trustpilot['Review_Title'].apply(CalcSentim)

#Plot relationship of sentiment with review stars
####################################################################################################

df_trustpilot['Review_Stars'].isna().sum()

#Plot sentiment scores vs TrustPilot review scores
sns.set_theme()

SentVsScore = df_trustpilot[['Review_Stars','TitleAndReview_Sentiment','Title_Sentiment','Review_Sentiment']]
SentVsScore = SentVsScore.groupby(['Review_Stars']).mean().reset_index()
SentVsScore_trans = pd.melt(SentVsScore, id_vars=['Review_Stars'],var_name='Sentiment Group',value_name='Avg_Sentiments')
SentVsScore_trans

plt.figure(figsize=(10,6))
sns.lineplot(data=SentVsScore_trans, x='Review_Stars',y='Avg_Sentiments', hue='Sentiment Group').set(title='Vader Sentiment Score vs TrustPilot Stars')
plt.xlabel('TrustPilot Stars')
plt.ylabel('Vader Sentiment Score')
plt.savefig('StarsVsSentiments.png')
plt.show()

#Export Data
####################################################################################################

#Rearrange cols
column_order = ['ReviewNum', 'Brand', 'From', 'Num_Of_Reviews', 'Experience_Date', 'Posted_DateTime','hour',
       'Review_Stars',  'Review_Title', 
       'Review_TitleAndText', 'Review_Type', 'KeyPhrases', 
       'TitleAndReview_Sentiment', 'Review_Sentiment', 'Title_Sentiment','url']

df_trustpilot = df_trustpilot.reindex(columns=column_order)


#Title and Review visually best? Although repetition in title and first line of text a concern?
#df_trustpilot = df_trustpilot.drop(columns=['Review_Text'])
df_trustpilot.to_json('sentimentdata.json')
df_trustpilot.to_csv('sentimentdata.csv',index=False)

