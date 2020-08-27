import requests
from bs4 import BeautifulSoup
import csv
import time

### for macOS ###
import ssl
import os
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
#################

### Home page url ###
url = 'https://food.ltn.com.tw/latest/1'

### header ###
headers = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
}

### 食譜CSV檔 ###
with open('./ltnfood.csv', 'w') as ltn:
    writeCsv = csv.writer(ltn)
    writeCsv.writerow(['食譜名稱', '食譜網址', '食譜食材', '圖片網址'])

pageNumber = 1
for pageNumber in range(1,543):

    ## request首頁
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    foodList = soup.select('div[class="recipelist boxTitle sort"] > a')

    for food in foodList:
        foodUrl = "https://food.ltn.com.tw/"+food["href"]
        foodName = food.span.text
        foodPic = food.img["src"]
        print(foodUrl)
        print(foodName)
        print(foodPic)

        ## request 食譜頁面
        res_food = requests.get(foodUrl, headers=headers)
        res_food.encoding='utf-8'
        soup_food = BeautifulSoup(res_food.text, 'html.parser')


        ingredients = []
        ingredientCol = soup_food.select('dl[class="recipe"] > dd')
        for ingredientL in ingredientCol:
            ingredient = ingredientL.text.replace('\t',' ').split('\n')
            ingredients = ingredients + ingredient
        if ingredients == []:
            ingredientCol = soup_food.select('ul[class="material"]> li')[1]
            ingredients = str(ingredientCol).strip('<li>' '</li>').split('<br/>')

        print(ingredients)
        print('-' * 10)


        with open('./ltnfood.csv', 'a') as ltn:
            writeCsv = csv.writer(ltn)
            writeCsv.writerow([foodName, foodUrl, ingredients, foodPic])

        time.sleep(5)

    pageNumber += 1
    url = f'https://food.ltn.com.tw/latest/{pageNumber}'
    time.sleep(10)