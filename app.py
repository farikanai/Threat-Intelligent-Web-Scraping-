from flask import Flask ,render_template ,request 
from urllib.request import urlopen
from urllib.error import HTTPError 
from urllib.error import URLError 
import requests
import os
import pandas as pd
import matplotlib.pyplot as plt
# import matplotlib.use('Agg')
import io
import base64
from textblob import TextBlob
import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import chardet
import csv
import pprint


from utils import scrape_content, load_existing_content,get_cyber_crime_feed, save_to_csv, read_from_file, data_cleaner, sentiment_trend

app = Flask(__name__, static_folder='static')
                
@app.route("/articles")
def articles():
    render_template(articles)
        
@app.route('/')
def index():
    if request.method == "GET": 
        array, box_count = scrape_content()
        return render_template('index.html', articles=array, count=box_count)

@app.route('/search_queries/', methods=["POST"])
def search_queries():

    results = []
    scrape_content = load_existing_content()
    for article in scrape_content[1]:
        if request.json['text'].lower() in article["description"].lower():
            results.append(article["description"])
    html = render_template("search_results.html", results=results)
    return {"html":html}

@app.route("/article")
def article(array,box_count):
    return array % box_count 



@app.route("/plots")
def show_plots():
    articles, box_count = get_cyber_crime_feed()
    save_to_csv(articles)
    data_cleaner()
    sentiment_trend()
    data = pd.read_csv('cleaned_file.csv', encoding='utf-8')

    # Ensure the 'Description' column is string type
    data['Description'] = data['Description'].astype(str)

    # Apply sentiment analysis
    data['Sentiment'] = data['Description'].apply(lambda x: TextBlob(x).sentiment.polarity)

    # Convert 'Date' column to datetime
    data['Date'] = pd.to_datetime(data['Date'], format='mixed',)

    # Save the data with the new 'Sentiment' column
    data.to_csv('cleaned_file1.csv', index=False)

    def save_plot_to_img(fig):
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img = base64.b64encode(buf.getvalue()).decode('utf-8')
        return img

    # Plot a histogram of the sentiment scores
    plt.figure(figsize=(10, 6))
    plt.hist(data['Sentiment'], bins=30, color='skyblue', edgecolor='black')
    plt.title('Histogram of Sentiment Scores')
    plt.xlabel('Sentiment Score')
    plt.ylabel('Frequency')
    hist_img = plt.show()
    plt.savefig('hist.png')
    hist_img= save_plot_to_img(plt)

    # # Plot a time series of the sentiment scores
    # plt.figure(figsize=(10, 6))
    # plt.plot_date(data['Date'], data['Sentiment'], linestyle='solid', marker=None)
    # plt.title('Time Series of Sentiment Scores')
    # plt.xlabel('Date')
    # plt.ylabel('Sentiment Score')
    # plt.show()

    # Plot a pie chart of the sentiment categories
    sentiment_categories = ['Positive' if score > 0 else 'Negative' if score < 0 else 'Neutral' for score in data['Sentiment']]
    sentiment_counts = pd.Series(sentiment_categories).value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=140)
    plt.title('Pie Chart of Sentiment Categories')
    # plt.show()
    pie_img = save_plot_to_img(plt)

    # Plot a bar chart of the average sentiment score per title
    average_sentiment_per_title = data.groupby('Title')['Sentiment'].mean()
    plt.figure(figsize=(10, 10))
    plt.bar(average_sentiment_per_title.index, average_sentiment_per_title.values, color='skyblue', edgecolor='black')
    plt.title('Bar Chart of Average Sentiment Score Per Title')
    plt.xlabel('Title')
    plt.ylabel('Average Sentiment Score')
    plt.xticks(rotation=90)
    # plt.show()
    bar_img = save_plot_to_img(plt)

    # print(hist_img,bar_img,pie_img )
    return render_template('plots.html', hist_img=hist_img, pie_img=pie_img, bar_img=bar_img)


if __name__ == "__main__":
    app.run(debug=True) 
