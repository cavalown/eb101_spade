import matplotlib
from matplotlib import pyplot as plt
import pandas as np
import pymysql
import pyimgur
import numpy as np

def search_item(user, sql):
    print(f"Now connecting to MySQL: 'IP'")
    connection = pymysql.connect(host='ip', port=3306, user='food2', passwd='mysqlfoodeb101', charset="utf8")
    cursor = connection.cursor()
    print(f"Now using database: i_member")
    # sql = f'SELECT nutrients,difference FROM i_member.everyday_nutrients_difference WHERE record_time=date(curdate()) AND m_id="{user}";'
    try:
        cursor.execute(sql)
        fetch = cursor.fetchall()
    except Exception as e:
        print(f'Something Wrong:\n\t\t\t{e}')
        return
    return fetch


def uploadImgur(path):
    CLIENT_ID = "bed634128600c00"
    PATH = path
    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title="Instant Nutrition Need")
    imgur_url = uploaded_image.link
    print('UpLoad success')
    return imgur_url


if __name__ == '__main__':
    user_id = 'M10000001'
    # 從MySQL找到USER所需一日營養素
    # Calories[0],Moisture[1],Protein[2],Saturated_fat[3],Carbohydrate[4]
    sql1 = f'SELECT nutrients,content FROM i_member.demand_schedule WHERE m_id="{user_id}"'
    nutritionNeed = search_item(user_id,sql1)[0:5]
    # print(nutritionN)
    # 從MySQL找到剩餘的營養需求
    # sql2 = f'SELECT nutrients,difference FROM i_member.everyday_nutrients_difference WHERE record_time=date(curdate()) AND m_id="{user_id}"'
    # nutritionLeft = search_item(user_id,sql2)[0:5]
    #假設的剩餘營養素需求
    nutritionL = [700,450,28,89,650]
    # 剩餘營養素需求文字
    nN = np.array(nutritionNeed)
    nL = np.array(nutritionL)
    showNuNeed = f"""
    <剩餘所需營養素>
    熱量:{nL[0]}(kcal)
    水份:{nL[1]}(ml)
    蛋白質:{nL[2]}(g)
    脂質:{nL[3]}(g)
    碳水化合物:{nL[4]}(g)
    """
    print(showNuNeed)
    # 畫累積長條圖圖資料
    x1 = ['Calories', 'Moisture', 'Protein', 'Saturated_fat', 'Carbohydrate']
    Y1 = (nN[:, 1] - nL) * 100 / nN[:, 1]
    Y2 = nL * 100 / nN[:, 1]
    plt.bar(x1, Y1, label='Demand Left %')
    plt.bar(x1, Y2, bottom=Y1, label='Eaten %')
    plt.legend()
    plt.savefig(f'ttt{user_id}.png')
    url1 = uploadImgur(f'ttt{user_id}.png')
    print(url1)

    # 畫雷達圖
    labels = np.array(['Calories', 'Moisture', 'Protein', 'Saturated_fat', 'Carbohydrate'])
    nAttr = 5
    data = np.array(Y1)  # 數據值
    angles = np.linspace(0, 2 * np.pi, nAttr, endpoint=False)
    data = np.concatenate((data, [data[0]]))
    angles = np.concatenate((angles, [angles[0]]))
    fig = plt.figure(facecolor="white")
    t = plt.subplot(111, polar=True)
    plt.plot(angles, data,'bo-', color ='g', linewidth = 2)
    plt.fill(angles, data, facecolor='g', alpha = 0.25)
    plt.thetagrids(angles * 180 / np.pi, labels)
    plt.figtext(0.52, 0.95, 'Currently Nutrition Taken(%)', ha ='right')
    plt.grid(True)
    # plt.show()
    plt.savefig(f'ggg{user_id}.png')
    url2 = uploadImgur(f'ggg{user_id}.png')
    print(url2)
