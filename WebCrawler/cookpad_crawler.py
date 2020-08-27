import requests
from bs4 import BeautifulSoup
import csv
import random
import time

### Home page url ###
url = 'https://cookpad.com/tw?after=1579940354.0'

### header ###
headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"}

### 食譜CSV檔 ###
with open('./cookpad.csv', 'w') as cp:
    writeCsv = csv.writer(cp)
    writeCsv.writerow(['食譜名稱', '葷素代碼', '食譜網址', '食譜食材', '圖片網址'])
### 食譜編號檔 ###
with open('./dishNoList.csv', 'w') as dn:
    writeCsv = csv.writer(dn)
    writeCsv.writerow(['食譜編號'])
i= 1
while True :
    ### request Home page ###
    res = requests.get(url, headers=headers)
    print('網頁擷取： ', res.status_code)
    print('=' * 50)

    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    # print(soup.prettify())

    ### select every dishes list in a page ###
    dishList = soup.select('div[class="p-3 feed__body"]')
    for dish in dishList:
        try:
            ## -食譜名稱- ##
            dish_select_Name = dish.a.h2
            dishName = dish_select_Name.text.strip()
            print('index:', i)
            print('食譜名稱： ', dishName)

            ## -食譜編號- ##
            dish_number = dish.find('a')["href"]
            dishNo= dish_number.split('/')[3].split('-')[0]
            print('食譜編號： ', dishNo)


            ## -食譜網址- ##
            dish_url = 'https://cookpad.com' + dish_number
            print('食譜網址： ', dish_url)

            ### request dish content page ###
            res_dish = requests.get(dish_url, headers=headers)
            print('食譜擷取： ', res.status_code)
            res_dish.encoding = 'utf-8'
            soup_dish = BeautifulSoup(res_dish.text, 'html.parser')

            ## -葷素- ##
            tagColumn=soup_dish.select('li[class="scroll-bar__item"]')
            tags = []
            eatType = ''
            for tag in tagColumn:
                tags.append(tag.text)

            if '全素' in tags:
                print('飲食葷素：  全素')
                eatType = 1
            elif '五辛素' in tags:
                print('飲食葷素：  五辛素')
                eatType = 2
            elif '蛋奶素' in tags:
                print('飲食葷素：  蛋奶素')
                eatType = 3
            else:
                print('飲食葷素：  葷食')
                eatType = 0

            ## -食譜食材- ##
            dish_ingredient = soup_dish.select('div[itemprop="ingredients"]')
            all_ingredients=[]
            for each_ingredient in dish_ingredient:
                ingredient=each_ingredient.text.strip()
                all_ingredients.append(ingredient)
            print('食譜食材： ', all_ingredients)

            ## -食譜照片- ##
            dish_pic = soup_dish.find(id="recipe_image").find('a')["href"]
            dish_pic_url = "https://cookpad.com" + dish_pic
            print('照片連結： ', dish_pic_url)
            print('='*50)

            ### 寫入CSV檔 ###
            with open('./cookpad.csv', 'a', newline='') as cp:
                writeCsv = csv.writer(cp)
                writeCsv.writerow([dishName, eatType, dish_url, all_ingredients, dish_pic_url])

            ### 寫入食譜編號 ###
            with open('./dishNoList.csv', 'a', newline='') as dn:
                writeCsv = csv.writer(dn)
                writeCsv.writerow([str(dishNo)])

            time.sleep(random.randint(5,10))

        except TypeError :
            print('"Here is TypeError"')

        except AttributeError:
            print('"Here is AttributeError"')

        except Exception:
            continue
        i += 1

    try:
        url_link = soup.find(id="feed_pagination").find('a')["href"]
        url = "https://cookpad.com" + url_link
        print('+++ Next page:', url)
        time.sleep(random.randint(10,15))
    except Exception:
        print('失敗', url)
        with open('./urlStop.txt', 'w') as st:
            st.write(url)
        break