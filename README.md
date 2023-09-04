# zillows_analysis

## Used API

"""
Zillow Scraper API(https://app.scrapeak.com/)

Search Listing `/listing`

| Parameter | Description                                                                                                                | Isrequired | Type   |
| --------- | -------------------------------------------------------------------------------------------------------------------------- | ---------- | ------ |
| api_key   | API_KEY                                                                                                                    | Yes        | String |
| url       | The URL of the listing page.<br>Includes the 'searchQueryState'.<br>Ensure it is valid.<br>It's used for specific actions. | Yes        | String |

Property Details `/property`

| Parameter | Description      | Isrequired | Type    |
| --------- | ---------------- | ---------- | ------- |
| api_key   | API_KEY          | Yes        | String  |
| zpid      | zpid or property | Yes        | Integer |

"""
