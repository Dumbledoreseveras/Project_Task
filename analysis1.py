# -*- coding: utf-8 -*-
"""analysis1.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qngBm5DLSE7JTOB6p2OK_9HZfBr5xT11
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import webbrowser
import os
from wordcloud import WordCloud

nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

apps_df = pd.read_csv('/content/Play Store Data.csv')
reviews_df = pd.read_csv('/content/User Reviews.csv')

#Generate a word cloud for the most frequent keywords found in 5-star reviews, but exclude common stopwords and app names. Additionally, filter the reviews to include only those from apps in the "Health & Fitness" category.

apps_df = apps_df.dropna(subset=['Rating'])
for column in apps_df.columns:
  apps_df[column].fillna(apps_df[column].mode()[0], inplace=True)
apps_df.drop_duplicates(inplace=True)
apps_df_rating = apps_df[apps_df['Rating']==5]
reviews_df.dropna(subset=['Translated_Review'],inplace=True)
apps_df[column].fillna(apps_df[column].mode()[0],inplace=True)

from wordcloud import WordCloud, STOPWORDS

nltk.download('stopwords')

reviews_df['Translated_Review'] = reviews_df['Translated_Review'].astype(str).str.replace(',','').str.replace('.','').str.replace('!','').str.replace('?','').str.replace(':','').astype(str)

apps_df_fitness = apps_df[apps_df['Category']=='Health & Fitness']
stop_words = set(STOPWORDS)

merged_df = reviews_df.merge(apps_df_fitness, on ='App', how='inner')

five_star = merged_df[merged_df['Rating'] == 5]['Translated_Review']
five_star_reviews = ' '.join(five_star)

import matplotlib.pyplot as plt

wordcloud = WordCloud(
    width=800, height=400,
    background_color='white',
    stopwords=stop_words,
    min_font_size=10
).generate(five_star_reviews)
plt.figure(figsize=(8, 8), facecolor=None)
plt.imshow(wordcloud)
plt.axis("off")
plt.tight_layout(pad=0)
plt.show()


# Visualize the sentiment distribution (positive, neutral, negative) of user reviews using a stacked bar chart, segmented by rating groups (e.g., 1-2 stars, 3-4 stars, 4-5 stars). Include only apps with more than 1,000 reviews and group by the top 5 categories

merged_df = pd.merge(apps_df, reviews_df, on='App', how='inner')
apps_df = apps_df.dropna(subset=['Reviews'])
apps_df['Reviews'] = apps_df['Reviews'].fillna(0)
apps_df['Reviews'] = apps_df['Reviews'].astype(int)

print(apps_df['Reviews'].dtype)

apps_df = apps_df[apps_df['Reviews']>1000]

apps_df = apps_df.dropna(subset=['Rating'])
for column in apps_df.columns :
    apps_df[column].fillna(apps_df[column].mode()[0],inplace=True)
apps_df.drop_duplicates(inplace=True)

category_counts = apps_df['Category'].value_counts().nlargest(5)

def rating_group(rating):
  if rating <= 2:
    return 'Average Rating'
  elif  2 < rating <= 4:
    return 'Above Average Rating'
  else:
    return 'Good Rating'
apps_df['rating_group'] = apps_df['Rating'].apply(rating_group)

reviews_df['Sentiment_Score'] = reviews_df['Translated_Review'].apply(lambda x: sia.polarity_scores(str(x))['compound'])

def sentiment_category(score):
    if score > 0.5:
        return 'Positive'
    elif score >= 0:
        return 'Neutral'
    else:
        return 'Negative'
reviews_df['Sentiment'] = reviews_df['Sentiment_Score'].apply(sentiment_category)
merged_df = pd.merge(apps_df, reviews_df, on='App', how='inner')

sentiment_distribution = merged_df.groupby(['rating_group', 'Sentiment']).size().unstack(fill_value=0).reset_index()
long_data = sentiment_distribution.melt(id_vars='rating_group', var_name='Sentiment', value_name='Reviews')

fig = px.bar(
    long_data,
    x='rating_group',         
    y='Reviews',     
    color='Sentiment',         
    title='Sentiment Distribution by Rating Groups',  
    labels={'rating_group': 'Rating Groups', 'Reviews': 'Number of Reviews'},
    text='Reviews'   
)

fig.update_layout(
    barmode='stack',          
    xaxis_title='Rating Groups',
    yaxis_title='Number of Reviews',
    legend_title='Sentiment',
    template='plotly_white'    
)
fig.show()

#Create a scatter plot to visualize the relationship between revenue and the number of installs for paid apps only. Add a trendline to show the correlation and color-code the points based on app categories.

apps_df = apps_df[apps_df['Type'] == 'Paid']
apps_df['Installs'] = pd.to_numeric(apps_df['Installs'].astype(str).str.replace(',','').str.replace('+','').str.replace('Free', '0').astype(int), errors='coerce')
apps_df['Price'] = apps_df['Price'].astype(str).str.replace('$', '').str.replace('Everyone', '0').astype(float)
apps_df['Revenue'] = apps_df['Price']*apps_df['Installs']

fig = px.scatter(
    apps_df,
    x='Revenue',
    y='Installs',
    color='Category',
    trendline='ols',
    title='Revenue vs. Installs (Paid Apps)',
    labels= {
        'Revenue': 'Revenue',
        'Installs': 'Installs'
    }
)
fig.show()

#Use a grouped bar chart to compare the average rating and total review count for the top 10 app categories by number of installs. Filter out any categories where the average rating is below 4.0 and size below 10 M and last update should be Jan month . this graph should work only between 3PM IST to 5 PM IST apart from that time we should not show this graph in dashboard itself

def convert_size(size):
  if 'M' in size:
    return float (size.replace('M',''))
  elif 'K' in size:
    return float (size.replace('K',''))/1024
  else:
    return np.nan
apps_df['Size'] = apps_df['Size'].apply(convert_size)

apps_df['Last Updated'] = pd.to_datetime(apps_df['Last Updated'], errors = 'coerce')
apps_df['Month'] = apps_df['Last Updated'].dt.month

apps_df['Installs'] = pd.to_numeric(apps_df['Installs'].astype(str).str.replace(',','').str.replace('+','').str.replace('Free', '0').astype(int), errors='coerce')

apps_df = apps_df[apps_df['Rating'] >= 4.0]
apps_df = apps_df[apps_df['Size'] >= 10.0]
apps_df = apps_df[apps_df['Month'] == 1]

filter_apps_df = apps_df[
    (apps_df['Rating'] >= 4.0) &
    (apps_df['Size'] >= 10.0) &
    (apps_df['Month'] == 1)
]
installs_by_category = filter_apps_df.groupby('Category')['Installs'].sum().nlargest(10).index
filtered_apps_df = filter_apps_df[filter_apps_df['Category'].isin(installs_by_category)]

grouped_category = filtered_apps_df.groupby('Category')
average_ratings = grouped_category['Rating'].mean()
total_reviews = grouped_category['Reviews'].sum()
category_stats = pd.DataFrame({
    'Category': average_ratings.index,
    'Average Rating': average_ratings.values,
    'Total Reviews': total_reviews.values
})

import pytz
from datetime import datetime

time_zone_ist = pytz.timezone('Asia/Kolkata')
time = datetime.now(time_zone_ist)

import plotly.graph_objects as go
if 15 <= time.hour <= 17:
  fig = go.Figure()

  fig.add_trace(go.Bar(
        x=category_stats['Category'],
        y=category_stats['Average Rating'],
        name='Average Rating',
        marker_color='skyblue'
    ))

  fig.add_trace(go.Bar(
        x=category_stats['Category'],
        y=category_stats['Total Reviews'],
        name='Total Reviews',
        marker_color='dodgerblue'
    ))

    
  fig.update_layout(
        title='Grouped Bar Chart: Average Rating and Total Reviews by Category',
        xaxis_title='Category',
        yaxis_title='Values',
        barmode='group',  
        xaxis_tickangle=-45,  
        template='plotly_white'
    )

  fig.show()
else:
    print('Graph not shown. Current time is outside the display window 3 PM to 5 PM IST.')

# Create a dual-axis chart comparing the average installs and revenue for free vs. paid apps within the top 3 app categories. Apply filters to exclude apps with fewer than 10,000 installs and revenue below $10,000 and android version should be more than 4.0 as well as size should be more than 15M and content rating should be Everyone and app name should not have more than 30 characters including space and special character .this graph should work only between 1 PM IST to 2 PM IST apart from that time we should not show this graph in dashboard itself

apps_df['Installs'] = apps_df['Installs'].astype(str).str.replace(',', '').str.replace('+', '').str.replace('Free', '0').astype(int)
apps_df['Price'] = apps_df['Price'].astype(str).str.replace('$', '').str.replace('Everyone', '0').astype(float)
apps_df['Revenue'] = apps_df['Price']*apps_df['Installs']
apps_df['Android Ver'] = pd.to_numeric(apps_df['Android Ver'].astype(str).str.extract('(\d+\.?\d*)', expand=False), errors='coerce')
def convert_size(size):
  if 'M' in size:
    return float (size.replace('M',''))
  elif 'K' in size:
    return float (size.replace('K',''))/1024
  else:
    return np.nan
apps_df['Size'] = apps_df['Size'].apply(convert_size)

apps_df = apps_df[apps_df['Installs'] <= 10000]
apps_df = apps_df[apps_df['Revenue'] <= 10000]
apps_df = apps_df[apps_df['Android Ver'] > 4.0]
apps_df = apps_df[apps_df['Content Rating'] == 'Everyone']
apps_df = apps_df[apps_df['Size'] >= 15]
apps_df = apps_df[apps_df['App'].str.len()<=30]

filtered_apps = apps_df[
    (apps_df['Installs'] <= 10000) &
    (apps_df['Revenue'] <= 10000) &
    (apps_df['Android Ver'] > 4.0) &
    (apps_df['Size'] >= 15) &
    (apps_df['Content Rating'] == 'Everyone') &
    (apps_df['App'].str.len() <= 30)
]
top_categories = apps_df['Category'].value_counts().nlargest(3).index
filtered_apps_df = apps_df[apps_df['Category'].isin(top_categories)]

grouped_by_category_type = filtered_apps_df.groupby(['Category','Type'])
selected_index = grouped_by_category_type[['Installs', 'Revenue']]
mean_of_data = selected_index.mean()
aggregate_data = mean_of_data.unstack()

import pytz
from datetime import datetime

time_zone_ist = pytz.timezone('Asia/Kolkata')
time = datetime.now(time_zone_ist)

import plotly.graph_objects as go
if 13<= time.hour<=14:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=aggregate_data.index, 
        y=aggregate_data[('Installs', 'Free')], 
        name='Free Installs', 
        marker_color='skyblue'
    ))
    fig.add_trace(go.Bar(
        x=aggregate_data.index, 
        y=aggregate_data[('Installs', 'Paid')], 
        name='Paid Installs', 
        marker_color='dodgerblue'
    ))

    
    fig.add_trace(go.Scatter(
        x=aggregate_data.index, 
        y=aggregate_data[('Revenue', 'Free')], 
        name='Free Revenue', 
        mode='lines+markers', 
        line=dict(color='orange')
    ))
    fig.add_trace(go.Scatter(
        x=aggregate_data.index, 
        y=aggregate_data[('Revenue', 'Paid')], 
        name='Paid Revenue', 
        mode='lines+markers', 
        line=dict(color='red')
    ))

    
    fig.update_layout(
        title='Comparison of Installs and Revenue (Free vs. Paid Apps)',
        xaxis_title='Category',
        yaxis_title='Values',
        barmode='group',  
        template='plotly_white'
    )

    
    fig.show()
else:
    print("Graph not shown. Current time is outside the display window (1 PM to 2 PM IST).")


# Create an interactive Choropleth map using Plotly to visualize global installs by Category. Apply filters to show data for only the top 5 app categories and highlight category where the number of installs exceeds 1 million. The app category should not start with the characters “A,” “C,” “G,” or “S.” This graph should work only between 6 PM IST and 8 PM IST; apart from that time, we should not show it in the dashboard itself.

apps_df['Installs'] = apps_df['Installs'].astype(str).str.replace(',', '').str.replace('+', '').str.replace('Free', '0').astype(int)
apps_df = apps_df[apps_df['Category'].str.startswith(('A', 'C', 'G', 'S'))]
apps_df = apps_df[apps_df['Installs'] > 1000000]

installs_by_category = apps_df[
    (apps_df['Category'].str.startswith(('A', 'C', 'G', 'S'))) &
    (apps_df['Installs'] > 1000000)
]

top_categories = apps_df['Category'].value_counts().nlargest(5).index
installs_by_category = installs_by_category[installs_by_category['Category'].isin(top_categories)]

import pytz
from datetime import datetime
time_zone_ist = pytz.timezone('Asia/Kolkata')
time = datetime.now(time_zone_ist)

if 18 <= time.hour <= 20:
  fig = px.choropleth(
      installs_by_category,
      locations = 'App',
      locationmode = 'country names',
      color = 'Installs',
      hover_name = 'Category',
      title = 'Global Installs By Category',
      color_continuous_scale = 'Viridis', 
  )
  fig.show()
else:
  print("The Choropleth map is not available outside the time window of 6 PM to 8 PM IST.")

   