# zillows_analysis

## Used API

Zillow Scraper API(https://app.scrapeak.com/)

Search Listing `/listing`

| Parameter | Description                                                           | Isrequired | Type   |
| --------- | --------------------------------------------------------------------- | ---------- | ------ |
| api_key   | API_KEY                                                               | Yes        | String |
| url       | The URL of the listing page<br> with the 'searchQueryState' parameter | Yes        | String |

Property Details `/property`

| Parameter | Description      | Isrequired | Type    |
| --------- | ---------------- | ---------- | ------- |
| api_key   | API_KEY          | Yes        | String  |
| zpid      | zpid or property | Yes        | Integer |
