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


#printing out the categories so it's easier to choose:
df0 = pd.DataFrame(columns=['category_id', 'category'])
for row in cur.execute('SELECT * FROM CATEGORIES;'):
    category_id = row[0]
    category = row[2]
    df0 = df0.append({'category_id' : category_id, 'category' : category} , ignore_index=True)
print(df0)

#getting the names of categories (not contained in maps table):
df1 = pd.DataFrame(columns=['country_id', 'country'])
#creating this for actual use:
list = list()
for row in cur.execute('SELECT * FROM COUNTRIES;'):
    country_id = row[0]
    country = row[1]
    df1 = df1.append({'country_id' : country_id, 'country' : country} , ignore_index=True)
    list.append(country_id)


df2 = pd.DataFrame(columns=['country_id', 'country', 'total', 'post2015', 'shapefiles', 'geodatabases']) #creates a new dataframe with the specified columns

category_id = int(input("Enter category ID: "))

for country_id in list:
    print("country_id: ", country_id)

    #finding the country that matches the country_id:
    for row in df1.itertuples():
        if row.country_id == country_id:
            country = row.country
            print(country)

    total = 0
    post2015 = 0
    shapefiles = 0
    geodatabase = 0

    for row in cur.execute('SELECT * FROM MAPS'):


        if row[1] == country_id:
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
        df2 = df2.append({'country_id' : country_id, 'country' : country, 'total' : total, 'post2015' : post2015 , 'shapefiles' : shapefiles , 'geodatabases' : geodatabase} , ignore_index=True)

print(df2)
print(category_id)

cur.execute('SELECT category FROM Categories WHERE id = ? ', (category_id, ))
category = cur.fetchone()[0].lower()
filename = "overview-" + category + ".csv"
df2.to_csv(filename)
print("All done. See csv file named ", filename, ".")
