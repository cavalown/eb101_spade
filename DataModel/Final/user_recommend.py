import pandas as pd
import numpy as np
import datetime
import time
import random
from scipy.spatial.distance import pdist
import pymysql


# Connect to MySQL ####################################################################################################
def mySQLcon(host='35.229.172.113', port=3306, user='food2', password='1234'):
    # host = host
    # port = port
    # user = table
    # password = password
    print(f"Now connecting to MySQL: {host}")
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, charset="utf8")
    cursor = connection.cursor()
    return cursor, connection


#  Search in MySQL ####################################################################################################
def search_item(db, item, table):
    host = '35.229.172.113'
    port = 3306
    user = 'food2'
    password = '1234'
    print(f"Now connecting to MySQL: {host}")
    connection = pymysql.connect(host=host, port=port, user=user, passwd=password, charset="utf8")
    cursor = connection.cursor()
    db = db
    item = item
    table = table
    print(f"Now using database: {db}")
    sql = f"SELECT {item} FROM {db}.{table};"
    try:
        cursor.execute(sql)
        fetch = cursor.fetchall()
    except Exception as e:
        print(f'Something Wrong:\n\t\t\t{e}')
        return
    return fetch


# Insert to MySQL #####################################################################################################
def insert(db, table, value):
    print(f"Now using database: {db}")
    sql = f"insert into {db}.{table} value('{value}')"
    try:
        cursor.execute(sql)
        connection.commit()
        print(f'Insert Done! \n Value:{value} to Table: {table}')

    except Exception as e:
        print(f'Some Error: \n\t\t\t{e}')
        return
    return cursor.fetchall()


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


# 用 scipy 套件計算各種距離(相似度) Way 1. ################################################################################
def distance(sample, userNu):
    userData = np.array(userNu)
    sampleData = np.array(sample)
    # Eucledian Distance #####
    ED_dict = dict()
    # print(sampleData)
    for eachSample in sampleData:
        # print(eachSample[:-1])
        X = np.vstack([userData, eachSample[:-1]])
        ED = pdist(X)
        # print(str(ED).strip('[').strip(']'))
        # print(eachSample.tolist())
        ED_dict[str(ED).strip('[').strip(']')] = eachSample.tolist()
    minED = min(ED_dict.keys())
    clusterED = ED_dict[minED][-1]
    # print(f'最小的Eucledian Distance：{minED}')
    # print(f'原始的樣本內容為：\n{ED_dict[minED]}')
    # print(f'Cluster:\t{clusterED}')
    # print('-' * 20)

    # Manhattan Distance #####
    MD_dict = dict()
    # print(sampleData)
    for eachSample in sampleData:
        # print(eachSample[:-1])
        X = np.vstack([userData, eachSample[:-1]])
        MD = pdist(X, 'cityblock')
        # print(str(MD).strip('[').strip(']'))
        # print(eachSample.tolist())
        MD_dict[str(MD).strip('[').strip(']')] = eachSample.tolist()
    minMD = min(MD_dict.keys())
    clusterMD = MD_dict[minMD][-1]
    # print(f'最小的Manhattan Distance：{minMD}')
    # print(f'原始的樣本內容為：\n{MD_dict[minMD]}')
    # print(f'Cluster:\t{clusterMD}')
    # print('-' * 20)

    # Chebyshev Distance #####
    CheD_dict = dict()
    # print(sampleData)
    for eachSample in sampleData:
        # print(eachSample[:-1])
        X = np.vstack([userData, eachSample[:-1]])
        CheD = pdist(X, 'chebyshev')
        # print(str(CheD).strip('[').strip(']'))
        # print(eachSample.tolist())
        CheD_dict[str(CheD).strip('[').strip(']')] = eachSample.tolist()
    minCheD = min(CheD_dict.keys())
    clusterCheD = CheD_dict[minCheD][-1]
    # print(f'最小的Chebyshev Distance：{minCheD}')
    # print(f'原始的樣本內容為：\n{CheD_dict[minCheD]}')
    # print(f'Cluster:\t{clusterCheD}')
    # print('-' * 20)

    # Minkowski Distance #####
    MinkD_dict = dict()
    # print(sampleData)
    for eachSample in sampleData:
        # print(eachSample[:-1])
        X = np.vstack([userData, eachSample[:-1]])
        MinkD = pdist(X, 'minkowski')
        # print(str(MinkD).strip('[').strip(']'))
        # print(eachSample.tolist())
        MinkD_dict[str(MinkD).strip('[').strip(']')] = eachSample.tolist()
    minMinkD = min(MinkD_dict.keys())
    clusterMinkD = MinkD_dict[minMinkD][-1]
    # print(f'最小的Minkowski Distance：{minMinkD}')
    # print(f'原始的樣本內容為：\n{MinkD_dict[minMinkD]}')
    # print(f'Cluster:\t{clusterMinkD}')
    # print('-' * 20)

    # Cosine Distance #####
    CosD_dict = dict()
    # print(sampleData)
    for eachSample in sampleData:
        # print(eachSample[:-1])
        X = np.vstack([userData, eachSample[:-1]])
        CosD = pdist(X, 'cosine')
        # print(str(CosD).strip('[').strip(']'))
        # print(eachSample.tolist())
        CosD_dict[str(CosD).strip('[').strip(']')] = eachSample.tolist()
    minCosD = min(CosD_dict.keys())
    clusterCosD = CosD_dict[minCosD][-1]
    # print(f'最小的Cosine Distance：{minCosD}')
    # print(f'原始的樣本內容為：\n{CosD_dict[minCosD]}')
    # print(f'Cluster:\t{clusterCosD}')
    # print('-' * 20)

    # 取五種相似度距離算出的群眾數 #####
    # print('根據五種距離相似度得到的結果：')
    # print(f'1. Eucledian Distance-> user cluster = {clusterED}')
    # print(f'2. Manhattan Distance-> user cluster = {clusterMD}')
    # print(f'3. Chebyshev Distance-> user cluster = {clusterCheD}')
    # print(f'4. Minkowski Distance-> user cluster = {clusterMinkD}')
    # print(f'5. Cosine Distance-> user cluster = {clusterCosD}')
    # print('=' * 20)
    counts = np.bincount([clusterED, clusterMD, clusterCheD, clusterMinkD, clusterCosD])
    modeNum = np.argmax(counts)
    # print(f'Cluster取眾數為：{modeNum}')
    return modeNum


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
    print(f'歐式距離分群：{userCluster_e}')
    print('-' * 20)

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
    print(f'曼哈頓距離分群：{userCluster_m}')
    print('-' * 20)

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
    print(f'柴比雪夫距離分群：{userCluster_che}')
    print('-' * 20)

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
    print(f'Minkowski距離分群：{userCluster_mi}')
    print('-' * 20)

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
    print(f'餘弦距離分群：{userCluster_cos}')
    print('-' * 20)

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

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 2:
        print('使用者為Cluster B的族群，推薦Cluster 5,1,4,6 的菜餚。')
        dish2 = pd.read_csv('DishWithCluster/people_c2_dish.csv')
        # advicePool = pd.concat([dish1, dish2, dish3, dish4], axis=0)
        for dishid in dish2.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 3:
        print('使用者為Cluster C的族群，推薦Cluster 7,6,3,1 的菜餚。')
        dish3 = pd.read_csv('DishWithCluster/people_c3_dish.csv')
        # advicePool = pd.concat([dish1, dish2, dish3, dish4], axis=0)
        for dishid in dish3.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 4:
        print('使用者為Cluster D的族群，推薦Cluster 7,3,2,1,4 的菜餚。')
        dish4 = pd.read_csv('DishWithCluster/people_c4_dish.csv')
        # advicePool, = pd.concat([dish1, dish2, dish3, dish4], axis=0)
        for dishid in dish4.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    # print(advices)
    return advices


# 總體的統計 ############################################################################################################
def rowData(path):
    data = pd.read_csv(path)
    dataS = data.iloc[:, [4, 5, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27]]
    dataV = np.array(dataS)
    Mean = np.mean(dataV, axis=0)
    Sigma = np.std(dataV, axis=0)
    #     Value = (dataV-Mean)/Sigma
    return Mean, Sigma


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

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 2:
        print('使用者目前狀況適合Cluster 2 的菜餚。')
        dish2 = pd.read_csv('DishWithCluster/dishCluster2.csv')
        for dishid in dish2.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 3:
        print('使用者目前狀況適合Cluster 3 的菜餚。')
        dish3 = pd.read_csv('DishWithCluster/dishCluster3.csv')
        for dishid in dish3.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 4:
        print('使用者目前狀況適合Cluster 4 的菜餚。')
        dish4 = pd.read_csv('DishWithCluster/dishCluster4.csv')
        for dishid in dish4.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 5:
        print('使用者目前狀況適合Cluster 5 的菜餚。')
        dish5 = pd.read_csv('DishWithCluster/dishCluster5.csv')
        for dishid in dish5.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 6:
        print('使用者目前狀況適合Cluster 6 的菜餚。')
        dish6 = pd.read_csv('DishWithCluster/dishCluster6.csv')
        for dishid in dish6.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    elif modeNum == 7:
        print('使用者目前狀況適合Cluster 7 的菜餚。')
        dish7 = pd.read_csv('DishWithCluster/dishCluster7.csv')
        for dishid in dish7.r_id:
            adviceSet.add(dishid)
            adviceList = list(adviceSet)

        advices = random.sample(adviceSet, k=5)

    return advices


if __name__ == '__main__':
    time_point1 = time.time()
    # 連線MySQL取出User輸入的基本資料
    userInput = search_item(db='i_member', item='*', table='member')[0]
    print(userInput)
    userBas = list(userInput)[2:7]
    print(f'User Basic info:\n{userBas}')
    print('-' * 20)

    # 換算User需求的Nutrition
    userNu = userBasicNu(userBas)
    print(f'User Nutrition Need:\n{userNu}')
    print('-' * 20)
    time_point2 = time.time()
    print(f'算出營養需求的時間：{time_point2 - time_point1}')

    # 準備需要拿來做相似度分析的sample data
    df = pd.read_csv('peopleSample_cluster.csv', index_col='X')
    data = df
    sample = df.iloc[:, 1:]

    # 進行五種距離計算，並取結果的眾數(Way 2)，決定User是哪一群！
    mini = distanceA(sample, userNu, data)
    print(f'User的Cluster為：{mini}')
    time_point3 = time.time()
    print(f'算出人相似群的時間：{time_point3 - time_point2}')

    # 這裡要寫一個判斷式，判斷是否當日有吃過東西了，如果沒有進行第一種推薦，有點會進行地二種推薦
    # 連接MySQL得到difference
    # 推薦第一餐（根據初始分群）
    advice = advise1(mini)
    time_point4 = time.time()
    print(f'推薦菜餚：{advice}')
    print(f'算出推薦第一餐的時間：{time_point4 - time_point3}')

    # 推薦其他餐 （根據剩餘需求和分群菜餚配對）
    # 假定剩餘需求
    nuNeed = pd.DataFrame(
        [1918.0, 1350.0, 49.5, 191.8, 1112.4, 27, 2400, 4700, 1000, 320, 15, 12, 800, 500, 12, 20.59, 100, 300])
    nuEat = pd.DataFrame([800, 250, 12, 33, 124, 1, 901, 2300, 243, 123, 2, 3, 321, 123, 4, 7, 43, 126])
    # print(nuNeed)
    # print(nuEat)
    leftNu = (np.array(nuNeed) - np.array(nuEat))
    # print(type(leftNu))
    # 準備好要標準化的資料
    all_mean = np.array(pd.read_csv('totalMean.csv', index_col=[0]))
    all_sigma = np.array(pd.read_csv('totalSigma.csv', index_col=[0]))
    clustersV = np.array(pd.read_csv('dish7clustersV.csv', index_col=[0]))
    # 將user剩餘的營養需求做標準化（用總體的統計資料）
    userLeft = (leftNu - all_mean) / all_sigma
    # print(all_mean)
    # print(all_sigma)
    # print(clustersV)
    # print(list(userLeft.flat))
    # 將使用者剩餘的營養需求向量和7個菜餚群做相似度分析
    cluster = distance2(list(userLeft.flat), clustersV)
    # print(cluster)
    # 推薦菜餚
    advicett = advise2(cluster)
    print(advicett)
    time_point5 = time.time()
    print(f'算出推薦第X餐的時間：{time_point5 - time_point4}')
