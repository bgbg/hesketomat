# Hesketomat 

## General notes

This project is a web application that is used to manage podcast episodes. 

 - The backend is built with FastAPI 
 - The frontend is built with Next.js
 - The database is built with [SQLite](https://www.sqlite.org/index.html) and is located in the `data` folder. 

 ## User interaction

The UI has to support Hebrew (right-to-left) and is Hebrew-first. Layout is important.
Element names in this document are in English, but the UI is in Hebrew, so the names should be translated.

The UI will have several tabs:

 ### Config 

 This tab is used to configure the app. It will show a table with a list of podcasts with the following columns:

 - Small image (scaled, not cropped)
 - Title
 - Description
 - RSS feed URL
 - Last updated (YY-MM-DD HH:MM)

 The user will be able to add a new podcast by pasting the RSS feed URL to a text box. If the URL is valid, the podcast will be added to the table. If the URL is not valid, the user will be notified. If the podcast is already in the table, the user will be notified. 

 ### Episodes

 This tab is used to manage the episodes of podcasts. It will show a table with a list of podcasts (thumbnail, title, number of available episodes), and the user will be able to select as many podcasts as they want.

 Clicking on a "refresh" button will fetch the latest episodes from the RSS feed and update the table.
 Clicking on "empty" will remove all the episode data from the database. Make this button red and small.

 The tab will contain a search bar and a set of two sliders. The sliders will be used to assign weights to the title and description of the episode. Each slider integer, will have a minimum value of 0 and a maximum value of 100. The default value is 50.

 The search bar will be used to search for episodes by title or description. The search will be case-insensitive and will be performed on the title and description of the episode. The user doesn't need to press enter, the search will be performed on every change, once the user stops typing for 0.5 seconds.

 Below the search bar and sliders, there will be a grid of cards, each card will represent an episode. The card will have the following elements:

 - Thumbnail (scaled, not cropped)
 - Publish date
 - Title
 - Description
 - "Copy url" button
 - Play button

 When the search bar is empty, the cards will be sorted by publish date, from newest to oldest. Otherwise, the cards will be sorted by relevance to the search query. The matches will be highlighted in the title and description. 

 ### More tabs
 The app will have more tabs in the future, the project is designed to be modular. Thus, add another tab, "More", and have a "Coming Soon" message in it.

 ## Backend

 The backend is built with FastAPI and is located in the `backend` folder. It is a REST API that is used to fetch the data from the database and to update the database. Each endpoint is documented and has at least one test (we use `pytest`).

## APIs used
- all the secrets are stored in .env



