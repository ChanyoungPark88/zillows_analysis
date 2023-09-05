# Zillow Analysis Tool

## 1. Project objective

The goal of the project is to select a city in the United States and retrieve housing information to analyze properties. The foundational data is scraped from Zillow. All housing information within the area is obtained through the Search Listing API, while detailed information on specific properties is sourced from the Property Details API.

## 2. Technical Stack

- Programming Language
  - Python: The primary language used for the main logic and data handling.
- Web Framework & Library
  - Streamlit: A Python library used to construct the frontend of the web application.
- Data Analysis & Processing
  - Pandas: A Python library used for data analysis and processing.
  - JSON: Used for data formatting and serialization.
- Database
  - MongoDB: A NoSQL database used for data storage and retrieval.
- Cloud Storage & Services
  - Google Cloud Storage: A cloud-based data storage service.
- Data Visualization
  - Plotly Express: A Python library used for chart and graph visualization.
- Utility & Miscellaneous Libraries
  - URllib: Used for URL encoding and processing.
  - Base64: Used for data encoding and decoding.
  - os.environ: Used for loading environment variables.
- API
  - Zillow Scraper API: A public API by Scrapeak, enabling data extraction of Listings and Property details directly from Zillow.

### 2.1 Used API

Zillow Scraper API(https://app.scrapeak.com/)

#### 2.1.1 Search Listing `/listing`

| Parameter | Description                                                           | Isrequired | Type   |
| --------- | --------------------------------------------------------------------- | ---------- | ------ |
| api_key   | API_KEY                                                               | Yes        | String |
| url       | The URL of the listing page<br> with the 'searchQueryState' parameter | Yes        | String |

#### 2.2.1 Property Details `/property`

| Parameter | Description      | Isrequired | Type    |
| --------- | ---------------- | ---------- | ------- |
| api_key   | API_KEY          | Yes        | String  |
| zpid      | zpid or property | Yes        | Integer |

## 3. Key Features

Users can select the desired feature from the sidebar:

- Listing
  - Users can select a state and city via dropdown menus.
  - Upon pressing the "Run" button, users can fetch a list of housing options available in the chosen area.
- Property
  - Users can enter the 'zpid' or address.
  - This allows users to retrieve detailed information about a specific property.
- Analysis
  - Users can view insights derived from the data obtained in both the "Listing" and "Property" sections.
  - This feature provides analysis based on specific criteria, offering a deeper understanding of the housing market trends and specifics.

## 4. Project Challenges & Solutions

Every project starts with a simple idea.

- Challenge 1: At first, I used a YouTube example that showed real estate info using Streamlit and API. But I wanted to copy the advanced features from a YouTuber's app. It wasn't easy.
  - Solution 1: I looked closely at the YouTuber's app and listed the important features. I used Pandas to clean the data from the API. Now, only the needed info is displayed to users.

While showing data, I felt we needed more.

- Challenge 2: While creating the website, I thought users should save and use their data safely.
  - Solution 2: To save data well, I chose MongoDB. For giving files to users, I used GCS. There was a problem with API keys. I fixed it with Streamlit's environment and base64. I checked GCS's guide to solve file upload problems.

There was one last step for users' convenience.

- Challenge 3: Even after making most of the app, users had to copy and paste the Zillow URL every time. It was not convenient.
  - Solution 3: To address this, I combined sample datasets from Zillow and SimpleData. I made one dataset. With this, the app creates URLs using state and city info by itself.

With these challenges, my project grew. Now, it boasts numerous features, making it user-friendly.

## 5. Performance Optimization & Security Measures

## 6. Screenshots & Demo Video

## 7. Learning Points from the Project
