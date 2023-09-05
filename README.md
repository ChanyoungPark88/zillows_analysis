# Zillow Analysis Tool

## 1. Project objective

The goal of the project is to select a city in the United States and retrieve housing information for property analysis. The data comes from Zillow. I use the Search Listing API to get all housing information in the area. For more details on a specific house, I use the Property Details API.

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
  - os.environ: Loads environment variables.
- API
  - Zillow Scraper API: Gets house data from Zillow.

### 2.1 Used API

Zillow Scraper API: https://app.scrapeak.com/

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

- Search Listings
  - Pick a state and city from lists.
  - Press "Run" to see house options in that area.
- Retrieve Property Details
  - Enter a 'zpid' or address to view house details. If they use a zpid or address from the same data row, they will see the same house details. This is due to both the zpid and address pointing to the same property listing on Zillow.
- Analysis
  - Look at data from the "Listing" and "Property" parts.
  - Learn more about house market trends.

## 4. Project Challenges & Solutions

- Challenge 1: At first, I followed a YouTube example. But I wanted to add more features.
  - Solution 1: I reviewed the application demonstrated in the YouTube tutorial and adopted the best features from it. I utilized Pandas to display only relevant information.
- Challenge 2: I wanted users to save and use their data safely.
  - Solution 2: I used MongoDB to save data. I employed GCS to allow users to download files. I had a problem with API keys but fixed it using Streamlit and base64.
- Challenge 3: Users had to type the Zillow URL every time.
  - Solution 3: I combined data from the Zillow and the SimpleData. The app now makes URLs using state and city info.

My project got better with each challenge

## 5. Performance Optimization & Security Measures

- Better Performance
  - Fast Data Handling: I use Pandas to process only needed data. This makes the app faster.
  - Easy URL Making: My app generates the Zillow URL for users. Users don't need to type it. This is easier and faster.
- Keeping API_KEY Safe:
  - I don't save API_KEYS in the code. I store them in Streamlit settings. This keeps them safe. While Base64 is not used for encryption, it's essential for data conversion, as Streamlit only accepts the 'TOML' format.

## 6. Screenshots & Demo Video

![Search Listings](https://storage.cloud.google.com/myproject-screenshots/Screen%20Recording%202023-09-04%20at%208.11.29%20PM.gif)
![Property Details](https://storage.cloud.google.com/myproject-screenshots/Screen%20Recording%202023-09-04%20at%208.21.40%20PM.gif)

## 7. Learning Points from the Project
