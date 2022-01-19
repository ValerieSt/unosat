import urllib.request, urllib.parse, urllib.error
import re
import time
from bs4 import BeautifulSoup
import ssl
from datetime import datetime

import sqlite3
#connection:
conn = sqlite3.connect('unosat-maps.sqlite')
#handle/responses:
cur = conn.cursor()

#make it easy to find start in terminal
print("------------------------------------------\n------------------------------------------\n------------------------------------------")

#ignore SSL certificate errors:
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

#creating an empty table 'Countries'
cur.execute('DROP TABLE IF EXISTS COUNTRIES')
cur.execute('CREATE TABLE COUNTRIES (id INTEGER NOT NULL PRIMARY KEY UNIQUE, name TEXT UNIQUE)')

startpage = "https://www.unitar.org/maps/countries"

html = urllib.request.urlopen(startpage, context=ctx).read()
soup = BeautifulSoup(html, "html.parser")

#for testing purposes

hrefs = soup.find_all('a')
for href in hrefs:
    hreftext = str(href)
    #find all links to countries
    if hreftext.find("/maps/countries/") != -1:

        countryid = re.findall("/maps/countries/([0-9]+)", hreftext)[0]
        countryname = href.text.strip()

        #santity checking:
        if countryid is None or countryname is None:
            continue
        cur.execute('''INSERT OR IGNORE INTO COUNTRIES(id, name)
        VALUES ( ?, ? )''', ( countryid, countryname ) )
        conn.commit()

#creating a new table called 'Categories'. Manually coding the category ids and abbreviations that will later be used in maps table.
cur.execute('DROP TABLE IF EXISTS Categories')
cur.execute('CREATE TABLE Categories(id INTEGER NOT NULL PRIMARY KEY UNIQUE, abbreviation TEXT UNIQUE, category TEXT UNIQUE)')
cur.execute("INSERT INTO categories VALUES(1,'AC','Technical disaster')")
cur.execute("INSERT INTO categories VALUES(2,'AV','Avalanche')")
cur.execute("INSERT INTO categories VALUES(3,'CE','Complex_Emergency')")
cur.execute("INSERT INTO categories VALUES(4,'DR','Drought')")
cur.execute("INSERT INTO categories VALUES(5,'EQ','Earthquake')")
cur.execute("INSERT INTO categories VALUES(6,'FL','Flood')")
cur.execute("INSERT INTO categories VALUES(7,'FR','Fire')")
cur.execute("INSERT INTO categories VALUES(8,'LS','Landslide')")
cur.execute("INSERT INTO categories VALUES(9,'OS','Oil Spill')")
cur.execute("INSERT INTO categories VALUES(10,'OT','Other')")
cur.execute("INSERT INTO categories VALUES(11,'RC','Refugee_Camp')")
cur.execute("INSERT INTO categories VALUES(12,'ST','Storm')")
cur.execute("INSERT INTO categories VALUES(13,'TC','Tropical_Cyclone')")
cur.execute("INSERT INTO categories VALUES(14,'TS','Tsunami')")
cur.execute("INSERT INTO categories VALUES(15,'VO','Volcano')")
cur.execute("INSERT INTO categories VALUES(99,'MS','Missing_or_Undefined')")
conn.commit()


#The maps table will be the main reference table, containing all information at the level of individual maps:
cur.execute('DROP TABLE IF EXISTS MAPS')
cur.execute('CREATE TABLE MAPS (id INTEGER NOT NULL PRIMARY KEY UNIQUE, country_id INTEGER, urls TEXT UNIQUE, glide TEXT, published_date TEXT, category_id INTEGER, shapefile INTEGER, shapefile_download TEXT, esri INTEGER, esri_download TEXT)')

# go through each row of the country database and creating a list that will later be iterated through (to avoid cur.execute statement as loop and inside the loop)
list = list()

for row in cur.execute('SELECT * FROM COUNTRIES;'):

    country_id = row[0]
    if country_id is None:
        continue
    list.append(country_id)

valid = 0
invalid = 0

for country_id in list:
    print("Country ID: ", country_id)

    url = "https://www.unitar.org/maps/countries/" + str(country_id)
    html = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html, "html.parser")

    hrefs = soup.find_all('a')
    #go through each href and check whether it contains 'current page'. If so, take the url
    count2 = 0
    for href in hrefs:
        hreftext = str(href)
        if hreftext.find("Go to page") != -1:
            #count each link that says 'go to page'
            count2 = count2 + 1
            #last page: total of 'go to page' mentions divided by two (because it displays them on top and on the bottom of the page):
        lastpage = int(count2/2)
    print("Number of sub-pages: ", (lastpage + 1))

    count3 = 0

    while (count3 < (lastpage + 1)):
        pageurl = url + "?page=" + str(count3)
        print("Going through ", pageurl)
        count3 = count3 + 1

        html = urllib.request.urlopen(pageurl, context=ctx).read()
        soup = BeautifulSoup(html, "html.parser")

        fieldcontent = soup.find_all('span', class_='field-content')
        print("Iterating through the map pages...")
        for content in fieldcontent:

            contenttext = str(content)
            #if it includes a link to /maps/map
            if contenttext.find("/maps/map/") != -1:
                #extract the map number (creates a list, but there should only be one element, so we're just taking the first element)
                mapnumber = re.findall("/maps/map/([0-9]+)", contenttext)[0]
                mapurl = "https://www.unitar.org/maps/map/" + str(mapnumber)
                html = urllib.request.urlopen(mapurl, context=ctx).read()
                soup = BeautifulSoup(html, "html.parser")
                if str(soup).find("Product not found") != -1:
                    continue
                valid = valid + 1

                divs = soup.find_all('div', class_="map-info-element")
                #esri and shapefile values starting with 0s for each map page, then updating to 1 if ref to shapefile / esri files is found.
                esri = 0
                shapefile = 0
                glide = None
                published = None

                for div in divs:

                    if str(div).find("Published") != -1:
                        published = re.findall("Published:\s+([0-9]+\s+[A-Za-z]+[,]\s+[0-9]+)", div.text)[0]
                        if (len(published) == 0):
                            published = "99"

                        else:
                            published = datetime.strptime(published, '%d %b, %Y')
                            published = published.date()

                    if str(div).find("GLIDE") != -1:
                        try:
                            glide = re.findall("GLIDE[:]\s+([A-Za-z0-9-]+)", div.text)[0]
                        except:
                            glide = "99"
                        #if no glide is found, assign value 99
                        if len(glide) == 0:
                            glide = "99"
                        #get category_id: from the categories table, select the category_id from the row where the first two letters of glide match the value for abbreviation:
                        cur.execute('SELECT id FROM Categories WHERE abbreviation = ? ', (glide[0:2], ))
                        try:
                            category_id = cur.fetchone()[0]
                        except:
                            category_id = 99

                    if str(div).find("Shapefile") != -1:
                        shapefile = 1
                        try:
                            shapefile_download = div.find('a')
                            #get the link from the a tag:
                            shapefile_download = shapefile_download.get('href')

                        except:
                            shapefile_download = "99"

                    if str(div).find("Geodatabase") != -1:
                        esri = 1
                        try:
                            #get the link from the a tag:
                            esri_download = div.find('a')
                            esri_download = esri_download.get('href')

                        except:
                            esri_download = "99"

                if esri == 0:
                    esri_download = "99"
                if shapefile == 0:
                    shapefile_download = "99"
                if published is None:
                    published = "99"
                if glide is None:
                    glide = "99"
                print(mapurl)
                print(glide)
                cur.execute('''INSERT OR IGNORE INTO MAPS(id, country_id, urls, glide, published_date, category_id, shapefile, shapefile_download, esri, esri_download)
                VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )''', ( mapnumber, country_id, mapurl, glide, published, category_id, shapefile, shapefile_download, esri, esri_download ) )
                conn.commit()

        time.sleep(0.5)
    print("One country done.")
    print("Taking a short rest.")
    time.sleep(1)
    print("Continuing...")

#close the connection
conn.close()
print("Valid links: ", valid)
print("All done. Check your tables in SQL")
