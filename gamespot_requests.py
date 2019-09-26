from pymongo import MongoClient
import requests
import pandas as pd

db_name = 'gamespot_reviews'
client = MongoClient('127.0.0.1', 27017)
# connect to the database
db = client[db_name]
# open the specific collection
reviews = db.reviews

headers = {
    "user_agent": "[YOUR USER AGENT] API Access"
}

games_base = "http://www.gamespot.com/api/games/?api_key=[YOUR API KEY HERE]&format=json"

pages = list(range(0, 14900))
pages_list = pages[0 : 14900: 100]

game_fields = "release_date,id,name,genres,themes,franchises"

def get_games(url_base ,num_pages, fields, collection):

    field_list = "&field_list=" + fields + "&sort=score:desc" + "&offset="

    for page in num_pages:
        url = url_base + field_list + str(page)
        print(url)
        response = requests.get(url, headers=headers).json()
        print(response)
        video_games = response['results']
        for i in video_games:
            collection.insert_one(i)
            print("Data Inserted")

review_base = "http://www.gamespot.com/api/reviews/?api_key=2bd1b212487bea64e2198ae432311f4b522ad1b5&format=json"
review_fields = "id,title,score,deck,body,good,bad"

get_games(review_base, pages_list, review_fields, reviews)

# To get another collection and join the collections

#get_games(games_base, pages_2, game_fields, games)

#{
#   $lookup:
#     {
#       from: <collection to join>,
#       localField: <field from the input documents>,
#       foreignField: <field from the documents of the "from" collection>,
#       as: <output array field>
#     }
#}

#pipeline = [
#    {'$lookup':
#                {'from': 'reviews',
#                 'localField': 'id',
#                 'foreignField': 'score',
#                 'as': 'score'}},
#             ]

#for doc in (games.aggregate(pipeline)):
#    print(doc)

scores = []

for score in list(reviews.find({}, {"_id":0, "score": 1})):
    scores.append(score)

print(scores[:900])

scores_data = pd.DataFrame(scores, index=None)
print(scores_data.head(15))