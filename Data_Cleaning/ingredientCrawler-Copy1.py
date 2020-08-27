import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import json

### for macOS ###
import ssl
import os
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
#################

### header ###
headers = {'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}

nameSet = set()
nicknameSet = set()
mySimiDict = {}

for pageNum in range(1,211):
    ### Home page url ###
    url = f'https://consumer.fda.gov.tw//Food/TFND.aspx?nodeID=178&p={pageNum}#ctl00_content_ListPanel'
    ## Test url
    # url = 'https://consumer.fda.gov.tw//Food/TFND.aspx?nodeID=178&p=13#ctl00_content_ListPanel'


    res = requests.get(url, headers=headers)
    print('網頁擷取： ', res.status_code)
    print('=' * 50)

    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # print(soup.prettify())

    ingredients = soup.select('tbody>tr')
    # print(ingredients)
    for ingredient in ingredients[1:]:
        # print(ingredient)
        items = ingredient.select('td')
        name = items[2]
        nicknames = items[3]
        name = name.text
        name = name.replace('平均值', '')
        name = name.split('(')[0]
        ## write name to csv
        # with open('./ingredientDict.csv', 'a', encoding='utf-8', newline='') as csvfile:
        #     writecsv = csv.writer(csvfile)
        #     writecsv.writerow([name])

        ## write into name set
        nameSet.add(name)

        nicknames = nicknames.text
        nicknames = nicknames.split(';')[0].split(',')
        # print(type(nicknames))
        print(nicknames)
        print(name)
        for nicknameall in nicknames:
            if '(' in nicknameall:
                nickname = nicknameall.split('(')[0]+nicknameall.split(')')[-1]
            else:
                nickname = nicknameall

            # print(nickname)
            # print(type(nickname))

            ## write nickname to csv
            # with open('./ingredientDict.csv','a',encoding='utf-8',newline='') as csvfile:
            #     writecsv = csv.writer(csvfile)
            #     writecsv.writerow([nickname])

            if nickname == '':
                continue
            else:
                mySimiDict[nickname] = name
                ## write into nickname set
                nicknameSet.add(nickname)

        mySimiDict[name] = name

        pageNum += 1
        print('-'*50)


## combind ingredient set
ingredientSet = nameSet|nicknameSet
# print('Name set:')
# print(nameSet)
# print('Nickname set:')
# print(nicknameSet)
# print('Ingredient set:')
# print(ingredientSet)
# print('My Similary Dictionary:')
# print(mySimiDict)

## make my cut dictionary in json
ingredientList = list(ingredientSet)
myCutDict = {}
for i in range(len(ingredientList)):
    key = ingredientList[i]
    myCutDict[key]=1

print(myCutDict)

with open('myCutDict.json','a',encoding='utf-8') as jsonfile:
    json.dump(myCutDict, jsonfile, ensure_ascii=False)
    jsonfile.write('\n')


## make my similary words dictionary
with open('mySimiDict.json','a',encoding='utf-8') as jsonfile:
    json.dump(mySimiDict, jsonfile, ensure_ascii=False)
    jsonfile.write('\n')