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


# 拉出每日營養差值表 #####################################################################################################
def get_difference(m_id):
    connection = pymysql.connect(host="IP", port=3306, user='food2', passwd='1234', db="i_member",
                                 charset="utf8")
    cursor = connection.cursor()
    # m_id = "M10000001"
    sql = f'SELECT nutrients,difference FROM i_member.everyday_nutrients_difference WHERE m_id = "{m_id}" AND record_time = "2020-07-10";'
    try:
        cursor.execute(sql)
        fetch = cursor.fetchall()
        nuDiff = []
        for item in fetch:
            eachNu = item[1]
            nuDiff.append(eachNu)
    except Exception as e:
        print(f'Something Wrong:\n{e}')
        return
    print(f"Get the Daily Nutrition Difference: \n{fetch}")
    return nuDiff


# 個體依據總體統計做標準化 #################################################################################################
def standardizationt(path, all_mean, all_sigma):
    data = pd.read_csv(path)
    dataS = data.iloc[:, [3, 4, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 26]]
    dataV = np.array(dataS)
    #     Mean = np.mean(dataV,axis=0)
    #     Sigma = np.std(dataV, axis=0)
    Value = (dataV - all_mean) / all_sigma
    return Value


# 剩餘營養素的相似度 #####################################################################################################
def distance2(userLeft, dishV):
    # Eucledian Distance #####
    ED_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        ED = pdist(X)
        ed = eachDishV.tolist()
        ED_dict[str(ED).strip('[').strip(']')] = f'{i}|{ed}'
        i += 1
    min_ED = min(ED_dict.keys())
    clusterED = ED_dict[min_ED].split('|')[0]

    # Manhattan Distance #####
    MD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        MD = pdist(X, 'cityblock')
        md = eachDishV.tolist()
        MD_dict[str(MD).strip('[').strip(']')] = f'{i}|{md}'
        i += 1
    min_MD = min(MD_dict.keys())
    clusterMD = MD_dict[min_MD].split('|')[0]

    # Chebyshev Distance #####
    CheD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        CheD = pdist(X, 'chebyshev')
        ched = eachDishV.tolist()
        CheD_dict[str(CheD).strip('[').strip(']')] = f'{i}|{ched}'
        i += 1
    min_CheD = min(CheD_dict.keys())
    clusterCheD = CheD_dict[min_CheD].split('|')[0]

    # Minkowski Distance #####
    MinkD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        MinkD = pdist(X, 'minkowski')
        minkd = eachDishV.tolist()
        MinkD_dict[str(MinkD).strip('[').strip(']')] = f'{i}|{minkd}'
        i += 1
    min_MinkD = min(MinkD_dict.keys())
    clusterMinkD = MinkD_dict[min_MinkD].split('|')[0]

    # Cosine Distance #####
    CosD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        CosD = pdist(X, 'cosine')
        cosd = eachDishV.tolist()
        CosD_dict[str(CosD).strip('[').strip(']')] = f'{i}|{cosd}'
        i += 1
    min_CosD = min(CosD_dict.keys())
    clusterCosD = CosD_dict[min_CosD].split('|')[0]

    # 取五種相似度距離算出的群眾數 #####
    print('根據五種距離相似度得到的結果：')
    print(f'1. Eucledian Distance-> user cluster = {clusterED}')
    print(f'2. Manhattan Distance-> user cluster = {clusterMD}')
    print(f'3. Chebyshev Distance-> user cluster = {clusterCheD}')
    print(f'4. Minkowski Distance-> user cluster = {clusterMinkD}')
    print(f'5. Cosine Distance-> user cluster = {clusterCosD}')
    print('=' * 20)
    counts = np.bincount([clusterED, clusterMD, clusterCheD, clusterMinkD, clusterCosD])
    modeNum = np.argmax(counts)
    # print(f'Cluster取眾數為：{modeNum}')
    return modeNum


# 第二餐以後的推薦 #######################################################################################################
def advise2(modeNum):
    adviceSet = set()
    adviceDish = []
    if modeNum == 1:
        print('使用者目前狀況適合Cluster 1 的菜餚。')
        dish1 = pd.read_csv('DishWithCluster/dishCluster1.csv')
        for dishid in dish1.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    elif modeNum == 2:
        print('使用者目前狀況適合Cluster 2 的菜餚。')
        dish2 = pd.read_csv('DishWithCluster/dishCluster2.csv')
        for dishid in dish2.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    elif modeNum == 3:
        print('使用者目前狀況適合Cluster 3 的菜餚。')
        dish3 = pd.read_csv('DishWithCluster/dishCluster3.csv')
        for dishid in dish3.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    elif modeNum == 4:
        print('使用者目前狀況適合Cluster 4 的菜餚。')
        dish4 = pd.read_csv('DishWithCluster/dishCluster4.csv')
        for dishid in dish4.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    elif modeNum == 5:
        print('使用者目前狀況適合Cluster 5 的菜餚。')
        dish5 = pd.read_csv('DishWithCluster/dishCluster5.csv')
        for dishid in dish5.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    elif modeNum == 6:
        print('使用者目前狀況適合Cluster 6 的菜餚。')
        dish6 = pd.read_csv('DishWithCluster/dishCluster6.csv')
        for dishid in dish6.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=9)

    elif modeNum == 7:
        print('使用者目前狀況適合Cluster 7 的菜餚。')
        dish7 = pd.read_csv('DishWithCluster/dishCluster7.csv')
        for dishid in dish7.r_id:
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
    props = {
        'bootstrap.servers': '35.201.205.44:9092',  # Kafka集群在那裡? (置換成要連接的Kafka集群)
        'group.id': 'otherRecommend',  # ConsumerGroup的名稱 (置換成你/妳的學員ID)
        'auto.offset.reset': 'earliest',  # Offset從最前面開始
        'session.timeout.ms': 6000,  # consumer超過6000ms沒有與kafka連線，會被認為掛掉了
        'error_cb': error_cb  # 設定接收error訊息的callback函數
    }
    consumer = Consumer(props)
    topicName = "dailyEat"
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
                        sys.stderr.write('ERROR!!!')
                    else:
                        # Error
                        raise KafkaException(record.error())
                else:
                    topic = record.topic()
                    partition = record.partition()
                    offset = record.offset()
                    timestamp = record.timestamp()
                    # msgKey = try_decode_utf8(record.key())
                    msgValue = try_decode_utf8(record.value())
                    count += 1
                    print('{}-{}-{} : ({})'.format(topic, partition, offset, msgValue))
                    # 連接MySQL得到difference
                    user_id = msgValue
                    getleftNu = get_difference(user_id)
                    leftNuL = []
                    for eachleftNu in getleftNu:
                        # print((eachleftNu))
                        leftNuL.append(float(eachleftNu))

                    leftNu = leftNuL[:-4] + [leftNuL[-1]]
                    # 準備好要標準化的資料
                    all_mean = np.array(pd.read_csv('totalMean.csv', index_col=[0]))
                    all_sigma = np.array(pd.read_csv('totalSigma.csv', index_col=[0]))
                    clustersV = np.array(pd.read_csv('dish7clustersV.csv', index_col=[0]))
                    all_meanV = list(all_mean.flat)
                    all_sigmaV = list(all_sigma.flat)
                    leftNuV = np.array(leftNu)
                    # 將user剩餘的營養需求做標準化（用總體的統計資料）
                    userLeft = (leftNuV - all_meanV) / all_sigmaV
                    # 將使用者剩餘的營養需求向量和7個菜餚群做相似度分析
                    cluster = distance2(list(userLeft.flat), clustersV)
                    # 推薦菜餚
                    print(f'下一餐推薦=>')
                    advice_more = advise2(cluster)
                    print(advice_more)
                    # 將推薦的下一餐菜餚存入MySQL
                    # update_recommend(user_id, advice_more)
                    update_recommend('M000000069',advice_more)
    except KeyboardInterrupt as e:
        sys.stderr.write('Aborted by user\n')
    except Exception as e:
        print(e)

    finally:
        consumer.close()
