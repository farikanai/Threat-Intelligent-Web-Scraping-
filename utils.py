import requests
import os
import pickle
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup
import time
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import chardet
import csv
import pprint
import pandas as pd
import re

scrape_pickle_path = "scrape.pickle"

def load_existing_content():
    content = None
    with Path(scrape_pickle_path).open("rb") as f:
        content = pickle.load(f)
    return content

def scrape_required():
    # pickle_path = Path(scrape_pickle_path)
    # return not pickle_path.exists()

    pickle_path = Path(scrape_pickle_path)
    if not pickle_path.exists():
        return True
    file_time = os.path.getmtime(scrape_pickle_path)
    # Check if the file is older than 24 hours
    return ((time.time() - file_time) / 3600 > 24)

def scrape_content():


    # First, check if there isn't already content that was recently
    # scrapped from the site to limit the calls made

    if scrape_required():

        url = 'https://thehackernews.com' 
        response = requests.get(url, headers={'User-Agent': 'WebSecApp'})
        soup = BeautifulSoup(response.text, 'html.parser')
        boxes = soup.find_all(class_ = 'clear home-right')
        box_count = 0
        array = []
        for box in boxes:
            title = box.find(class_ = 'home-title').get_text()
            description = box.find(class_= 'home-desc').get_text() 
            array.append({"title":title, "description":description}) 
            box_count += 1


        with Path(scrape_pickle_path).open("wb") as f:
            pickle.dump(
                [datetime.now(), array], f
            )

    else:
        time_stamp, array =  load_existing_content()
        box_count = len(array)

    return array, box_count

def get_cyber_crime_feed():
    articles = []
    box_count =  0
    url = 'https://thehackernews.com/'
     #' https://thehackernews.com/'
    
    ''' user agent to to prevent blocking :D, next challenge pagination '''
    response = requests.get(url, headers={'User-Agent': 'WebsecApp'}) 
    soup = BeautifulSoup(response.text, 'html.parser')
    boxes = soup.find_all(class_='clear home-right')
    
    for  box in boxes:
        title = box.find(class_='home-title')
        category = box.find(class_='h-tags')
        date = box.find(class_='h-datetime')
        description = box.find(class_='home-desc')
        if title and date and description:
            title = title.get_text()
            date = date.get_text()
            description = description.get_text()
            category = category.get_text() if category else 'Unknown'
            articles.append([date, category, title, description])
            box_count +=  1
    
    
    return articles, box_count

def save_to_csv(data):

    """    RSave  content from the webscraper  to csv (title, date ,description
    """
    with open("helil.csv", 'a',newline='', encoding="utf-8") as  csvfile:
         # Create a CSV writer object
        writer = csv.writer(csvfile)
        
        # Write the header if the file is new
        if csvfile.tell() == 0:
            writer.writerow(['Date', 'Category', 'Title', 'Description'])
        
        # Write each article
        for item in data:
            writer.writerow(item)
def read_from_file(data):

    """    Reads content from the specified file and returns it as a list of strings,
    where each string represents a line from the file.
    """
    try:
        # Read articles from CSV file
        with open("helil.csv", 'r', newline='', encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            content = list(reader)
            print("Content from CSV file:")
            pprint(content)
    except FileNotFoundError:
        print(f"File {'helil.csv'} not found.")
        return []

def data_cleaner():
    # Define a function to clean a string
    def clean_string(s):
        # Ensure s is a string
        if not isinstance(s, str):
            s = str(s)
        # Remove non-text characters
        return re.sub(r'\W+', ' ', s)

    # Read the CSV file
    df = pd.read_csv('helil.csv')

    # Apply the cleaning function to each cell in the DataFrame
    df = df.applymap(clean_string)

    # Save the cleaned DataFrame to a new CSV file
    df.to_csv('cleaned_file.csv', index=False)

    # Print a success message
    print("The CSV file was successfully cleaned and saved as cleaned_file.csv")

def sentiment_trend():
    #figure out file encoding 
    rawdata = open('helil.csv', 'rb').read()
    result = chardet.detect(rawdata)
    encoding = result['encoding']

    data = pd.read_csv('helil.csv', encoding=encoding)
    # Load the data
    # data = pd.read_csv('articles.csv')

    # Apply sentiment analysis using TextBlob
    data['Sentiment'] = data['Description'].apply(lambda x: TextBlob(x).sentiment.polarity)

    # Apply topic modeling using TF-IDF and LDA
    tfidf = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
    tfidf_matrix = tfidf.fit_transform(data['Description'])

    lda = LatentDirichletAllocation(n_components=5, random_state=42)
    lda.fit(tfidf_matrix)

    # Display the results
    sentiment_results = data[['Description', 'Sentiment']]
    topic_results = lda.components_
    sentiment_results.head(), topic_results

    df_processed = pd.DataFrame(sentiment_results)

    # Save the processed results to a CSV file
    df_processed.to_csv('processed_results.csv', index=False)




