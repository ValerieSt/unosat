# unosat

*unosat-maps.py*
Script to crawl the UNOSAT library for information on all publicly available maps, including the link to the map, the country name, the date the map was published, event category (complex emergency, landslide, flood etc.), 

Requirements: BeautifulSoup, sqlite3 

Outputs sql tables with all the information.

*overview-unosat-maps.py*
*overview-by-country.py*
*overview-by-category.py*

Once the sql tables are downloaded, you can use these scripts to gain an overview of the maps by country and category. Kept this very simple for now, this could be adapted to automatically download the shapefiles or geodatabases.
