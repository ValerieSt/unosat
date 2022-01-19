import urllib.request, urllib.parse, urllib.error
import re
import time
from bs4 import BeautifulSoup
import ssl
from datetime import datetime
import pandas as pd

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



#printing names of countries so it's easier to choose:
df0 = pd.DataFrame(columns=['country_id', 'country'])
for row in cur.execute('SELECT * FROM COUNTRIES;'):
    country_id = row[0]
    country = row[1]
    df0 = df0.append({'country_id' : country_id, 'country' : country} , ignore_index=True)
print(df0)
#getting the names of categories (not contained in maps table):
df1 = pd.DataFrame(columns=['category_id', 'category'])
for row in cur.execute('SELECT * FROM CATEGORIES;'):
    category_id = row[0]
    category = row[2]
    df1 = df1.append({'category_id' : category_id, 'category' : category} , ignore_index=True)


df2 = pd.DataFrame(columns=['category_id', 'category', 'total', 'post2015', 'shapefiles', 'geodatabases']) #creates a new dataframe with the specified columns

country_id = input("Enter the country ID: ")

for category_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 99]:
    print("CategoryID: ", category_id)

    #finding the category that matches the category_id:
    for row in df1.itertuples():
        if row.category_id == category_id:
            category = row.category
            print(category)

    total = 0
    post2015 = 0
    shapefiles = 0
    geodatabase = 0

    for row in cur.execute('SELECT * FROM MAPS WHERE country_id = ? ', (country_id, )):


        if row[5] == category_id:
            total = total + 1
            published = int(row[4][0:4])

            if published > 2015:

                post2015 = post2015 + 1
                if row[6] == 1:
                    shapefiles = shapefiles + 1
                if row[8] == 1:
                    geodatabase = geodatabase + 1
    if (post2015 + shapefiles + geodatabase) > 0:
        df2 = df2.append({'category_id' : category_id, 'category' : category, 'total' : total, 'post2015' : post2015 , 'shapefiles' : shapefiles , 'geodatabases' : geodatabase} , ignore_index=True)
print(df2)


cur.execute('SELECT name FROM Countries WHERE id = ? ', (country_id, ))
country = cur.fetchone()[0].lower()
filename = "overview-" + country + ".csv"
df2.to_csv(filename)
print("All done. See csv file named ", filename, ".")
