from confluent_kafka import Consumer, KafkaException, KafkaError
import sys
import pandas as pd
import numpy as np
import datetime
import time
import random
from scipy.spatial.distance import pdist
import pymysql


def error_cb(err):
    print('Error: %s' % err)


# 轉換msgKey或msgValue成為utf-8的字串
def try_decode_utf8(data):
    if data:
        return data.decode('utf-8')
    else:
        return None


# 指定要從哪個partition, offset開始讀資料
def my_assign(consumer_instance, partitions):
    for p in partitions:
        p.offset = 0
    print('assign', partitions)
    consumer_instance.assign(partitions)


# 根據基本資料換算成營養素需求 #############################################################################################
def userBasicNu(X):
    # info: #####
    sex = int(X[0])
    birth = str(X[1])
    height = float(X[2])
    weight = float(X[3])
    goal = X[-1][-1]

    today = datetime.datetime.today()
    birthday = datetime.datetime.strptime(birth, '%Y%m%d')
    age = int((today - birthday).days / 365)
    bmi = round(weight / float((height / 100) ** 2), 1)

    # nutrition need: ######
    # fixed
    na, k, ca, p, ve, vc, chol = 2400, 4700, 1000, 800, 12, 100, 300
    cal = round((23.1811 + 2.2589 * sex - 0.01807 * age - 0.1448 * weight + 0.03797 * height) * 1.9 * weight, 1)
    moi = round(weight * 30, 1)
    pro = (round(weight * 1.1, 1) if age < 71 else round(weight * 1.2, 1))
    sf = round(cal * 0.1, 1)
    car = round(cal * 0.58, 1)
    fs = round(cal * 0.1, 1)
    fm = round(cal * 0.06, 1)
    fp = round(cal * 0.009, 1)

    # sex leads nutrition
    if sex == 0:
        zn, va, vb = 12, 500, 20.59
        if age < 51:
            dif, mg, fe = 27, 320, 15
        elif 50 < age < 71:
            dif, mg, fe = 25, 310, 10
        else:
            dif, mg, fe = 24, 300, 10
    else:
        zn, va, vb, fe = 15, 600, 23.25, 10
        if age < 51:
            dif, mg = 34, 300
        elif 50 < age < 71:
            dif, mg = 32, 360
        else:
            dif, mg = 30, 350
    # goal leads nutrition
    # goal 1: normal
    # goal 2: lose weight
    if goal == 2:
        car = round(car * 0.34, 2)
        pro = round(pro * 1.67, 2)
        sf = round(sf * 2, 2)
    # goal 3: increase weight
    elif goal == 3:
        cal = round(cal * 1.5, 2)
        car = round(car * 1.5 * 0.95, 2)
        pro = round(pro * 1.5 * 1.39, 2)
        sf = round(sf * 1.5 * 0.8, 2)
        fs = round(fs * 1.5, 2)
        fm = round(fm * 1.5, 2)
        fp = round(fp * 1.5, 2)
    # goal 4: increase muscle
    elif goal == 4:
        cal = round(cal * 1.2, 2)
        car = round(car * 1.2 * 0.95, 2)
        pro = round(pro * 1.2 * 1.39, 2)
        sf = round(sf * 1.2 * 0.8, 2)
        fs = round(fs * 1.2, 2)
        fm = round(fm * 1.2, 2)
        fp = round(fp * 1.2, 2)
    # goal 5: ketogenic diet
    elif goal == 5:
        car = round(car * 0.09, 2)
        pro = round(pro * 1.11, 2)
        sf = round(sf * 3, 2)

    userNu = [sex, age, height, weight, bmi, cal, moi, pro, sf, car, dif, na, k, ca, mg, fe, zn, p, \
              va, ve, vb, vc, fs, fm, fp, chol]
    return userNu


# 將換算的營養素需求存入 MySQL的 demand_schedule TABLE 中 ##########################################################################
def insert_demand_schedule(m_id, demand_list):
    connection = pymysql.connect(host="IP", port=3306, user='food2', passwd='1234', db="testt",
                                 charset="utf8")
    group = demand_list[0]  # list[0] 即是 pr_group 對應數值
    # 主要執行的 SQL
    sql = f"""
    INSERT INTO testt.demand_schedule_test
        (ds_time, m_id, m_group, nutrients, content)
    VALUES	
        (CURDATE(), "{m_id}", "{group}", "Calories(kcal)", {demand_list[1]}),
        (CURDATE(), "{m_id}", "{group}", "Moisture(g)", {demand_list[2]}),
        (CURDATE(), "{m_id}", "{group}", "Protein(g)", {demand_list[3]}),	
        (CURDATE(), "{m_id}", "{group}", "Saturated_fat(g)", {demand_list[4]}),
        (CURDATE(), "{m_id}", "{group}", "Carbohydrate(g)", {demand_list[5]}),
        (CURDATE(), "{m_id}", "{group}", "Dietary_fiber(g)", {demand_list[6]}),
        (CURDATE(), "{m_id}", "{group}", "Na(mg)", {demand_list[7]}),
        (CURDATE(), "{m_id}", "{group}", "K(mg)", {demand_list[8]}),
        (CURDATE(), "{m_id}", "{group}", "Ca(mg)", {demand_list[9]}),
        (CURDATE(), "{m_id}", "{group}", "Mg(mg)", {demand_list[10]}),
        (CURDATE(), "{m_id}", "{group}", "Fe(mg)", {demand_list[11]}),
        (CURDATE(), "{m_id}", "{group}", "Zn(mg)", {demand_list[12]}),
        (CURDATE(), "{m_id}", "{group}", "P(mg)", {demand_list[13]}),
        (CURDATE(), "{m_id}", "{group}", "VitaminA(IU)", {demand_list[14]}),
        (CURDATE(), "{m_id}", "{group}", "VitaminE(mg)", {demand_list[15]}),
        (CURDATE(), "{m_id}", "{group}", "VitaminB_group", {demand_list[16]}),
        (CURDATE(), "{m_id}", "{group}", "VitaminC(mg)", {demand_list[17]}),
        (CURDATE(), "{m_id}", "{group}", "Fatty_acid_S(mg)", {demand_list[18]}),
        (CURDATE(), "{m_id}", "{group}", "Fatty_acid_M(mg)", {demand_list[19]}),
        (CURDATE(), "{m_id}", "{group}", "Fatty_acid_P(mg)", {demand_list[20]}),
        (CURDATE(), "{m_id}", "{group}", "Cholesterol(mg)", {demand_list[21]});    
    """
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()
    print("demand_Data INSERT to MySQL successfully")


# 用 scipy 套件計算各種距離(相似度) Way 2. ################################################################################
def distanceA(sample, userNu, data):
    userNu = np.array(userNu)
    sample = np.array(sample)[:, :-1]
    # print(userNu)
    # print(sample)
    ### Eucledian Distance
    minED = [100000000000]
    content1 = []
    for eachSample in sample:
        #     print(eachSample)
        X = np.vstack([userNu, eachSample])
        ED = pdist(X)
        if ED < minED[0]:
            minED = ED
            content1 = eachSample

    # print('E Distance:', minED[0])
    # print('Sample content:', content1)
    # print('Cluster:')
    cluster = data[data.Sex == content1[0]][data.Age == content1[1]][data.Height == content1[2]][
        data.BMI == content1[4]].Cluster
    userCluster_e = cluster.iloc[0]
    # print(f'歐式距離分群：{userCluster_e}')
    # print('-' * 20)

    # Manhattan Distance
    minMD = [100000000000]
    content2 = []
    for eachSample in sample:
        # print(eachSample)
        X = np.vstack([userNu, eachSample])
        MD = pdist(X, 'cityblock')
        if MD < minMD[0]:
            minMD = MD
            content2 = eachSample

    # print('M Distance:', minED[0])
    # print('Sample content:', content2)
    # print('Cluster:')
    cluster = data[data.Sex == content2[0]][data.Age == content2[1]][data.Height == content2[2]][
        data.BMI == content2[4]].Cluster
    userCluster_m = cluster.iloc[0]
    # print(f'曼哈頓距離分群：{userCluster_m}')
    # print('-' * 20)

    # Chebyshev Distance
    minCD = [100000000000]
    content3 = []
    for eachSample in sample:
        # print(eachSample)
        X = np.vstack([userNu, eachSample])
        CD = pdist(X, 'chebyshev')
        if CD < minCD[0]:
            minCD = CD
            content3 = eachSample

    # print('Che Distance:', minCD[0])
    # print('Sample content:', content3)
    # print('Cluster:')
    cluster = data[data.Sex == content1[0]][data.Age == content3[1]][data.Height == content3[2]][
        data.BMI == content3[4]].Cluster
    userCluster_che = cluster.iloc[0]
    # print(f'柴比雪夫距離分群：{userCluster_che}')
    # print('-' * 20)

    # Minkowski Distance
    minMiD = [100000000000]
    content4 = []
    for eachSample in sample:
        # print(eachSample)
        X = np.vstack([userNu, eachSample])
        MiD = pdist(X, 'minkowski', p=2)
        if MiD < minMiD[0]:
            minMiD = MiD
            content4 = eachSample

    # print('Mi Distance:', minMiD[0])
    # print('Sample content:', content4)
    # print('Cluster:')
    cluster = data[data.Sex == content4[0]][data.Age == content4[1]][data.Height == content4[2]][
        data.BMI == content4[4]].Cluster
    userCluster_mi = cluster.iloc[0]
    # print(f'Minkowski距離分群：{userCluster_mi}')
    # print('-' * 20)

    # Cosine Distance
    minMiD = [100000000000]
    content5 = []
    for eachSample in sample:
        # print(eachSample)
        X = np.vstack([userNu, eachSample])
        MiD = pdist(X, 'cosine')
        if MiD < minMiD[0]:
            minMiD = MiD
            content5 = eachSample

    # print('Cos Distance:', minMiD[0])
    # print('Sample content:', content4)
    # print('Cluster:')
    cluster = data[data.Sex == content5[0]][data.Age == content5[1]][data.Height == content5[2]][
        data.BMI == content5[4]].Cluster
    userCluster_cos = cluster.iloc[0]
    # print(f'餘弦距離分群：{userCluster_cos}')
    # print('-' * 20)

    print('根據五種距離相似度得到的結果：')
    print('1. Eucledian Distance-> user cluster = ', userCluster_e)
    print('2. Manhattan Distance-> user cluster = ', userCluster_m)
    print('3. Chebyshev Distance-> user cluster = ', userCluster_che)
    print('4. Minkowski Distance-> user cluster = ', userCluster_mi)
    print('5. Cosine Distance-> user cluster = ', userCluster_cos)
    print('-' * 50)
    counts = np.bincount([userCluster_e, userCluster_m, userCluster_che, userCluster_mi, userCluster_cos])
    # 返回众数
    modeNum = np.argmax(counts)
    print('Cluster取眾數為：', modeNum)
    return modeNum


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

    elif modeNum == 4:
        print('使用者為Cluster D的族群，推薦Cluster 7,3,2,1,4 的菜餚。')
        dish4 = pd.read_csv('DishWithCluster/people_c4_dish.csv')
        # advicePool, = pd.concat([dish1, dish2, dish3, dish4], axis=0)
        for dishid in dish4.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    # print(advices)
    return advices

# 將推薦的菜餚存入 MySQL的 recommend TABLE 中 ##########################################################################
def insert_recommend(userID,adviceDish):
    connection = pymysql.connect(host="IP", port=3306, user='food2', passwd='1234', db="testt",
                                 charset="utf8")
    # 主要執行的 SQL
    i = 1
    for r_id in adviceDish:
        # print(f'{user_id}\n{i}\n{r_id}')
        sql = f"""INSERT INTO testt.recommend_test
                    (m_id, r_order, r_id)
                    VALUES
                    ("{userID}", {i}, {r_id});"""
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        i += 1
    connection.close()
    print("demand_Data INSERT to MySQL successfully")

if __name__ == '__main__':
    props = {
        'bootstrap.servers': '35.201.205.44:9092',
        'group.id': 'newUserRecommend',
        'auto.offset.reset': 'earliest',
        'session.timeout.ms': 6000,
        'error_cb': error_cb
    }
    consumer = Consumer(props)
    topicName = "newUser"
    consumer.subscribe([topicName])
    count = 0
    try:
        while True:
            records = consumer.consume(num_messages=500, timeout=1.0)
            if records is None:
                continue

            for record in records:
                if record is None:
                    continue
                if record.error():
                    # Error or event
                    if record.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write('ERROR!')
                    else:
                        # Error
                        raise KafkaException(record.error())
                else:
                    topic = record.topic()
                    partition = record.partition()
                    offset = record.offset()
                    timestamp = record.timestamp()
                    msgKey = try_decode_utf8(record.key())
                    msgValue = try_decode_utf8(record.value())
                    count += 1
                    print(f'{topic}-{partition}-{offset} : ({msgKey} , {msgValue})')
                    # 換算User需求的Nutrition
                    newUI = msgValue.split('|')[1:]
                    user_id = msgValue.split('|')[0]
                    userNu = userBasicNu(newUI)
                    # 準備需要拿來做相似度分析的sample data
                    df = pd.read_csv('peopleSample_cluster.csv', index_col='X')
                    data = df
                    sample = df.iloc[:, 1:]
                    # 進行五種距離計算，並取結果的眾數(Way 2)，決定User是哪一群！
                    mini = distanceA(sample, userNu, data)
                    print(f'User的基礎Cluster為：{mini}')
                    # 紀錄Nutrition Need and cluster to MySQL
                    demand_list = [f'pr_group_{mini.tolist()}'] + userNu[5:]
                    print(demand_list)
                    insert_demand_schedule(user_id, demand_list)
                    print(f'User 營養素需求和基礎分群已寫進MySQL的"demand_schedule"')
                    recommendDish = advise1(mini)
                    #將New User第一餐的推薦寫入MySQL的recommend裡
                    insert_recommend(user_id, recommendDish)

    except KeyboardInterrupt as e:
        sys.stderr.write('Aborted by user\n')
    except Exception as e:
        print(e)
    finally:
        consumer.close()
