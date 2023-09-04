# Zillow Analysis Tool

## 1. Project objective

The objective of the project is to select a city in the United States and retrieve housing information in order to analyze properties. The foundational data is scraped from Zillow. All housing information within the area is obtained through the Search Listing API, while detailed information on specific properties is sourced from the Property Details API.

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
