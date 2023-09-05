# Zillow Analysis Tool

## 1. Project objective

The objective of the project is to select a city in the United States and retrieve housing information in order to analyze properties. The foundational data is scraped from Zillow. All housing information within the area is obtained through the Search Listing API, while detailed information on specific properties is sourced from the Property Details API.

## 2. Technical Stack

- Programming Language
  - Python: The primary language used for overall logic and data processing.
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

## 3. Key Features

## 4. Challenges & Solutions

## 5. Performance Optimization & Security Measures

## 6. Screenshots & Demo Video

## 7. Learning Points from the Project

## 2. Used API

Zillow Scraper API(https://app.scrapeak.com/)

### 2.1. Search Listing `/listing`

| Parameter | Description                                                           | Isrequired | Type   |
| --------- | --------------------------------------------------------------------- | ---------- | ------ |
| api_key   | API_KEY                                                               | Yes        | String |
| url       | The URL of the listing page<br> with the 'searchQueryState' parameter | Yes        | String |

### 2.2. Property Details `/property`

| Parameter | Description      | Isrequired | Type    |
| --------- | ---------------- | ---------- | ------- |
| api_key   | API_KEY          | Yes        | String  |
| zpid      | zpid or property | Yes        | Integer |
