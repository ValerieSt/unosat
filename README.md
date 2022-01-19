# unosat

*unosat-maps.py*

Script to crawl the UNOSAT library for information on all publicly available maps, including the link to the map, the country name, the date the map was published, event category (complex emergency, landslide, flood etc.), 

Requirements: BeautifulSoup, sqlite3 

Outputs sql tables with all the information.


Once the sql tables are downloaded, you can use *overview-by-country.py* or *overview-by-category.py* to gain an overview of the maps by country and category (might be adapted to automatically download the shapefiles or geodatabases.)
