from pymongo import MongoClient
import pymongo
import pandas as pd
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import string
import en_core_web_sm
import seaborn as sns

d_name = 'gamespot_reviews'
collection_name = 'gamespot'

client = MongoClient('127.0.0.1', 27017)
db = client[d_name]

reviews = db.reviews

# Declare lists to store data
scores = []
#decks = []
review_bodies = []

# Select data from collections

# Score data
for score in list(reviews.find({}, {"_id":0, "score": 1})):
    scores.append(score)

# How to get other fields
#for deck in list(reviews.find({}, {"_id":0, "deck": 1}).sort("score", pymongo.DESCENDING).limit(50)):
#    decks.append(deck)

# Review body data
#for body in list(reviews.find({}, {"_id":0, "body": 1}).sort("score", pymongo.DESCENDING).limit(40)):
#    review_bodies.append(body)

scores_data = pd.DataFrame(scores, index=None)
#decks_data = pd.DataFrame(decks, index=None)

reviews_data = pd.DataFrame(review_bodies, index=None)

def extract_comments(input):
    soup = BeautifulSoup(str(input), "html.parser")
    comments = soup.find_all('p')
    return comments

review_entries = extract_comments(str(review_bodies))
#print(review_entries[:500])

stop_words = set(stopwords.words('english'))

def filter_entries(entries, stopwords):

    text_entries = BeautifulSoup(str(entries), "lxml").text
    subbed_entries = re.sub('[^A-Za-z0-9]+', ' ', text_entries)
    split_entries = subbed_entries.split()

    stop_words = stopwords

    entries_words = []

    for word in split_entries:
        if word not in stop_words:
            entries_words.append(word)

    return entries_words

review_words = filter_entries(review_entries, stop_words)
print(review_words[:400])
review_words = review_words[5000:]
print(review_words[:400])

# Create word clouds

def make_wordcloud(data, title = None):
    wordcloud = WordCloud(background_color='black',
        max_words=250,
        max_font_size=40,
        scale=3,
        random_state=19
    ).generate(str(data))

    fig = plt.figure(1, figsize=(15, 15))
    plt.axis('off')

    if title:
        fig.suptitle(title, fontsize=20)
        fig.subplots_adjust(top=2.3)

    plt.imshow(wordcloud)
    plt.show()

make_wordcloud(review_words)

# Count most common words

translator = str.maketrans('','', string.punctuation)

def get_word_counts(words_list):
    word_count = {}

    for word in words_list:
        word = word.translate(translator).lower()
        if word not in stop_words:
            if word not in word_count:
                word_count[word] = 1
            else:
                word_count[word] += 1

    return word_count

review_word_count = get_word_counts(review_words)
review_word_count = Counter(review_word_count)
review_list = review_word_count.most_common()
print(review_list)

# Named entity recognition

nlp = en_core_web_sm.load()

doc = nlp(str(review_words))
labels = [x.label_ for x in doc.ents]
items = [x.text for x in doc.ents]

print([(X.text, X.label_) for X in doc.ents])
print(Counter(labels))
print(Counter(items).most_common(20))

def word_counter(doc, ent_name, col_name):
    ent_list = []
    for ent in doc.ents:
        if ent.label_ == ent_name:
            ent_list.append(ent.text)
    df = pd.DataFrame(data=ent_list, columns=[col_name])
    return df

review_persons = word_counter(doc, 'PERSON', 'Named Entities')
review_org = word_counter(doc, 'ORG', 'Organizations')
review_gpe = word_counter(doc, 'GPE', 'GPEs')

def plot_categories(column, df, num):
    sns.countplot(x=column, data=df,
                  order=df[column].value_counts().iloc[0:num].index)
    plt.xticks(rotation=-45)
    plt.show()

plot_categories("Named Entities", review_persons, 30)
plot_categories("Organizations", review_org, 30)
plot_categories("GPEs", review_gpe, 30)

# Visualize spread of review scores

scores = pd.DataFrame(scores, index=None).reset_index()
print(scores.head(20))

counts = scores['score'].value_counts()
print(counts.keys)

sns.countplot(x="score", data=scores)
plt.xticks(rotation=-90)
plt.show()