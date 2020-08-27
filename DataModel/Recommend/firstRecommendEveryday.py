from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import pymysql
import datetime
import random
import pandas as pd


def getUserCluster():
    connection = pymysql.connect(host='IP', port=3306, user='food2', passwd='1234', charset="utf8")
    cursor = connection.cursor()
    sql = f"SELECT DISTINCT m_id,m_group FROM i_member.demand_schedule;"
    try:
        cursor.execute(sql)
        fetch = cursor.fetchall()
    except Exception as e:
        print(f'Something Wrong:\n{e}')
        return
    return fetch


# 第一餐推薦 ############################################################################################################
def advise1(modeNum):
    adviceSet = set()
    adviceDish = []
    if modeNum == 1:
        print('使用者為Cluster A的族群，推薦Cluster 7,3,4 的菜餚。')
        dish1 = pd.read_csv('DishWithCluster/people_c1_dish.csv')
        # advicePool = pd.concat([dish1, dish2, dish3], axis=0)
        for dishid in dish1.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    elif modeNum == 2:
        print('使用者為Cluster B的族群，推薦Cluster 5,1,4,6 的菜餚。')
        dish2 = pd.read_csv('DishWithCluster/people_c2_dish.csv')
        # advicePool = pd.concat([dish1, dish2, dish3, dish4], axis=0)
        for dishid in dish2.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)
        advices = random.sample(adviceSet, k=9)
    elif modeNum == 3:
        print('使用者為Cluster C的族群，推薦Cluster 7,6,3,1 的菜餚。')
        dish3 = pd.read_csv('DishWithCluster/people_c3_dish.csv')
        # advicePool = pd.concat([dish1, dish2, dish3, dish4], axis=0)
        for dishid in dish3.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)
        advices = random.sample(adviceSet, k=9)
    else:
        # modeNum == 4
        print('使用者為Cluster D的族群，推薦Cluster 7,3,2,1,4 的菜餚。')
        dish4 = pd.read_csv('DishWithCluster/people_c4_dish.csv')
        # advicePool, = pd.concat([dish1, dish2, dish3, dish4], axis=0)
        for dishid in dish4.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)
        advices = random.sample(adviceSet, k=9)
    return advices


# 將推薦的菜餚存入 MySQL的 recommend TABLE 中 ##########################################################################
def update_recommend(userID, adviceDish):
    connection = pymysql.connect(host="IP", port=3306, user='food2', passwd='1234', db="testt",
                                 charset="utf8")
    i = 1
    for r_id in adviceDish:
        cursor = connection.cursor()
        sql1 = f"""SET SQL_SAFE_UPDATES=0;"""
        sql2 = f"""UPDATE testt.recommend_test SET r_id ={r_id}  WHERE m_id = "{userID}" AND r_order = {i};"""
        sql3 = f"""SET SQL_SAFE_UPDATES=1;"""
        cursor.execute(sql1)
        cursor.execute(sql2)
        cursor.execute(sql3)
        connection.commit()
        i += 1
    connection.close()
    print("demand_Data INSERT to MySQL successfully")



if __name__ == '__main__':
    while 1:
        # TIME = datetime.datetime.now()
        # if TIME.hour == 0 and TIME.minute == 0:
            user = getUserCluster()
            for eachUser in user:
               user_id = eachUser[0]
               user_cluster = eachUser[1].split('_')[-1]
               print(f'ID:{user_id}')
               adviseDish = advise1(user_cluster)
               print(adviseDish)
               update_recommend(user_id,adviseDish)

