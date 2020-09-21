# Nama: Wulandari
# Email: wulanddarii18@gmail.com


# Import Library
import tweepy
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import datetime
from datetime import timedelta

# Inisiasi variable dan query
database_name = "Data_Twitter.db"
create_twitter_table = '''CREATE TABLE IF NOT EXISTS twitter (
                            Id INTEGER PRIMARY KEY AUTOINCREMENT,
                            User_acc TEXT NOT NULL,
                            Date DATETIME NOT NULL,
                            Tweet TEXT NOT NULL UNIQUE, 
                            Sentiment INTEGER);'''
                            
update_twitter = '''INSERT OR IGNORE into twitter (User_acc, Date, Tweet) values (?,?,?);'''
update_sentiment = '''UPDATE twitter SET Sentiment = (?) WHERE Id = (?);'''
read_data = '''SELECT Id, Tweet
                    FROM twitter'''
select_data = '''SELECT User_acc, Date, Tweet, Sentiment
                    FROM twitter
                    WHERE DATE(Date) BETWEEN (?) AND (?);'''

consumer_key = 'oFTqcktlhHYhtBUQYvEXSYNGb'
consumer_secret = 'iQHyyAnkXyi2T2Xato1BCXTj8hdYbJG08f4L6PsCCpeLRtVYe2'
access_token = '2737082058-J03kdrXTtL6qOYZr4meuyDPBx1AHdtcSHpoBpkO'
access_token_secret = 'mUMZCtJffUVv2NHZ5iuZUqpzLAYgRjRbz19K725gxoMnv'
date = datetime.date.today()
twodays = datetime.timedelta(days=2)
range_date = date - twodays
search_word = 'vaksin covid'

# Read positive and negative files
pos_list= open("./kata_positif.txt","r")
pos_word = pos_list.readlines()
neg_list= open("./kata_negatif.txt","r")
neg_word = neg_list.readlines()

# Make a Database and Table
def make_table(database_name, create_twitter_table):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(create_twitter_table)
    connection.commit()
    cursor.close()
    connection.close()

make_table(database_name, create_twitter_table)

# Scraping Data
def get_data(consumer_key, consumer_secret, access_token, access_token_secret, search_word, range_date):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)

	new_search = search_word + " -filter:retweets"

	tweets = tweepy.Cursor(api.search,
			        q=new_search,
			        lang="id",
			        since=range_date).items(800)
		
	data = []
	for item in tweets:
		tweet = []
		user_acc = item.user.screen_name
		date = item.created_at
		tweet_clean = (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", item.text).split()))
		tweet.append(user_acc)
		tweet.append(date)
		tweet.append(tweet_clean)
		data.append(tuple(tweet))
	return(data)

# Update Tweet Data
def update_tweet(database_name, update_twitter, data):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.executemany(update_twitter,data)
    connection.commit()
    cursor.close()
    connection.close()

# Read SQL
def read_sql(database_name, read_data):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(read_data)
    tweet_ = list(cursor.fetchall())
    connection.commit()
    cursor.close()
    connection.close()
    return(tweet_)

# Calculate Sentiment Value
def sentiment_value(tweet_, pos_word, neg_word):
    Id_ = [list_[0] for list_ in tweet_]
    items = [list_[1] for list_ in tweet_]
    Sentiment = []
    for item in items:
        count_p = 0
        count_n = 0
        for word_pos in pos_word:
            if word_pos.strip() in item:
                count_p +=1
        for word_neg in neg_word:
            if word_neg.strip() in item:
                count_n +=1    
        Sentiment.append((count_p - count_n))
      
    id_ = []
    for number in Id_:
        id_.append(number)
    Sentiment_results = list(zip(Sentiment, id_))
    return(Sentiment_results)

# Updating Sentiment Value
def update_sentiment_column(database_name, update_sentiment, Sentiment):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.executemany(update_sentiment, (Sentiment))
    connection.commit()
    cursor.close()
    connection.close()


# Display Data
def display_data(database_name, select_data, date1, date2):
    connection = sqlite3.connect(database_name)
    cursor = connection.cursor()
    cursor.execute(select_data, (date1, date2))
    record = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return(record)

# Make a DataFrame
def df(record):
    df_ = []
    for row in record:
        list_ = [row[0], row[1], row[2]]
        df_.append(list_)
    data_display = pd.DataFrame(df_, columns=['User_acc','Date','Tweet'])
    print(data_display)
    return(data_display)

# Visualization
def visualization(record):
    #values = [value[0] for value in Sentiment_results]
    df_ = []
    for row in record:
        list_ = row[3]
        df_.append(list_)
    mean = np.mean(df_)
    median = np.median(df_)
    std = np.std(df_, ddof=1)
    print('Mean Value:', mean)
    print('Median Value:', median)
    print('Standard Deviation:', std)
    labels, counts = np.unique(df_, return_counts=True)

    plt.figure(0)
    plt.bar(labels, counts, align='center')
    plt.gca().set_xticks(labels)
    plt.xlabel('Sentiment Value')
    plt.ylabel('Count')
    plt.show()


# User Input
index = 0
while index < np.inf: 
    choice = input('''What do you want to do?
                    1. Update Data
                    2. Update Sentiment Value
                    3. View Data
                    4. Sentiment Visualization
                    5. Exit
                    Your Input:''')
    if choice == '1':
        data = get_data(consumer_key, consumer_secret, access_token, access_token_secret, search_word, range_date)
        update_tweet(database_name, update_twitter, data)
        print('Your data have been updated!')
    if choice == '2':
        tweet_ = read_sql(database_name, read_data)
        Sentiment = sentiment_value(tweet_, pos_word, neg_word)
        update_sentiment_column(database_name, update_sentiment, Sentiment)
        print('Sentiment values have been updated!')
    if choice == '3':
        date1 = input('Start date (format: 2020-08-15):')
        date2 = input('End date (format: 2020-08-15):')
        record = display_data(database_name, select_data, date1, date2)
        df(record)
    if choice == '4':
        date1 = input('Start date (format: 2020-08-15):')
        date2 = input('End date (format: 2020-08-15):')
        record = display_data(database_name, select_data, date1, date2)
        visualization(record)
    if choice == '5':
        print('You exit from the app!')
        break

