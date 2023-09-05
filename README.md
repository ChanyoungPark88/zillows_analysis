# Zillow Analysis Tool

## 1. Project objective

The goal of the project is to select a city in the United States and retrieve housing information to analyze properties. The data comes from Zillow. I use the Search Listing API to get all housing information in the area. For more details on a specific house, I use the Property Details API.

## 2. Technical Stack

- Programming Language
  - Python: Used for main tasks and handling data.
- Web Framework & Library
  - Streamlit: Helps build the website.
- Data Analysis & Processing
  - Pandas: Used to view and edit data.
  - JSON: Helps format the data.
- Database
  - MongoDB: Saves and gets the data.
- Cloud Storage & Services
  - Google Cloud Storage: A place in the cloud to save data.
- Data Visualization
  - Plotly Express: Helps show data in charts.
- Utility & Miscellaneous Libraries
  - URllib: Works with URLs.
  - Base64: Helps change data format.
  - os.environ: Loads settings.
- API
  - Zillow Scraper API: Gets house data from Zillow.

### 2.1 Used API

Zillow Scraper API(https://app.scrapeak.com/)

#### 2.1.1 Search Listing `/listing`

| Parameter | Description                                        | Isrequired | Type   |
| --------- | -------------------------------------------------- | ---------- | ------ |
| api_key   | API_KEY                                            | Yes        | String |
| url       | Listing page URL with the 'searchQueryState' value | Yes        | String |

#### 2.2.1 Property Details `/property`

| Parameter | Description      | Isrequired | Type    |
| --------- | ---------------- | ---------- | ------- |
| api_key   | API_KEY          | Yes        | String  |
| zpid      | zpid or property | Yes        | Integer |

## 3. Key Features

Users can:

- Listing
  - Pick a state and city from lists.
  - Press "Run" to see house options in that area.
- Property
  - Type in a 'zpid' or an address to see details about a house. If they use a zpid or address from the same data row, they will see the same house details. This is because both point to the same house on Zillow.
- Analysis
  - Look at data from the "Listing" and "Property" parts.
  - Learn more about house market trends.

## 4. Project Challenges & Solutions

- Challenge 1: At first, I implemented a YouTube example. But I wanted to add more features.
  - Solution 1: I looked at the YouTube app and picked the best features. I used Pandas to show only important data.
- Challenge 2: I wanted users to save and use their data safely.
  - Solution 2: I used MongoDB to save data. I used GCS to let users download files. I had a problem with API keys but fixed it using Streamlit and base64.
- Challenge 3: Users had to type the Zillow URL every time.
  - Solution 3: I combined Zillow and SimpleData data. The app now makes URLs using state and city info.

My project got better with each challenge

## 5. Performance Optimization & Security Measures

- Better Performance
  - Fast Data Handling: I use Pandas to show only needed data. This makes the app faster.
  - Easy URL Making: Our app makes the Zillow URL. Users don't need to type it. This is easier and faster.
- Keeping API_KEY Safe:
  - I don't save API_KEYS in the code. I save them in Streamlit settings. This keeps them safe. Base64 is not for safety. It's because Streamlit only takes data in the 'motl' format. Base64 makes the data into this format.

## 6. Screenshots & Demo Video

## 7. Learning Points from the Project
