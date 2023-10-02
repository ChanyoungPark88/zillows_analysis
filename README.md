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

### 4-1. Automating URL generation for API usage

- **Situation**: I needed specific filtered URLs for API usage and wanted to automate a task that was previously done manually.
  - **Task**: My goal was to create a mechanism where users wouldn't have to type the entire Zillow URL every time.
  - **Action**: I decided to parameterize the country and state information using a dropdown menu. By analyzing the URL pattern, I developed a feature that would update only the necessary information and auto-generate the URL.
  - **Result**: Users can now easily obtain a filtered URL by simply selecting the country and state from the dropdown, enhancing the user experience.

### 4-2. Displaying essential information on the website using Pandas

- **Situation**: I wanted to present important information on the website utilizing Pandas.
  - **Task**: To achieve this, I believed there was a need to load the actual files on the platform.
  - **Action**: I opted to use Google Cloud Service and MongoDB. Data scraped via the URL was processed by Pandas and then saved as files in cloud storage. Meanwhile, metadata for displaying the file list was stored in MongoDB, facilitating a seamless upload and download process for the files.
  - **Result**: I successfully integrated Pandas, Google Cloud Service, and MongoDB, providing users with a seamless way to view, upload, and download essential data on the website.

### 4-3. Data Post-processing for Scraped Data

- **Situation**: The data I scraped through the API contained many tables that appeared redundant or unnecessary for analysis. There were issues with duplicate tables and data entries with null values.
  - **Task**: I aimed to efficiently handle these redundancies and clean the data to be ready for analysis.
  - **Action**: Using Pandas, I conducted an analysis of the table columns. I then developed Python functions to handle null values and other post-processing needs.
  - **Result**: The dataset was successfully cleaned, with all redundancies removed and null values addressed, making it more streamlined for further analysis.

### 4-4. Managing Access Keys for APIs, MongoDB, and Google Cloud Service

- **Situation**: To utilize the API, MongoDB, and Google Cloud Service, specific access keys were required. Directly embedding these keys in the code presented a security risk.
  - **Task**: I needed a method to securely manage and utilize these access keys without compromising their confidentiality.
  - **Action**: I opted to implement these keys as parameters within the Streamlit web platform. Furthermore, to enhance security, I encoded the keys, ensuring they couldn't be easily deciphered.
  - **Result**: The integration of access keys became secure and manageable without posing any threat to the system's security.

## 5. Performance Optimization & Security Measures

- Better Performance
  - Fast Data Handling: I use Pandas to process only needed data. This makes the app faster.
  - Easy URL Making: My app generates the Zillow URL for users. Users don't need to type it. This is easier and faster.
- Keeping API_KEY Safe:
  - I don't save API_KEYS in the code. I store them in Streamlit settings. This keeps them safe. While Base64 is not used for encryption, it's essential for data conversion, as Streamlit only accepts the 'TOML' format.

## 6. Screenshots & Demo Video

## 7. Learning Points from the Project
