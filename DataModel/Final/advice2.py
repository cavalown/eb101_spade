import pandas as pd
import statistics as stat
import numpy as np
from scipy.spatial.distance import pdist
import time

path0 = 'DishWithCluster/dish_clusters.csv'
path1 = 'DishWithCluster/dishCluster1.csv'
path2 = 'DishWithCluster/dishCluster2.csv'
path3 = 'DishWithCluster/dishCluster3.csv'
path4 = 'DishWithCluster/dishCluster4.csv'
path5 = 'DishWithCluster/dishCluster5.csv'
path6 = 'DishWithCluster/dishCluster6.csv'
path7 = 'DishWithCluster/dishCluster7.csv'

'''
[Calories(kcal),Moisture(g),Protein(g),Saturated_fat(g),Carbohydrate(g),
Dietary_fiber(g),Na(mg),K(mg),Ca(mg),Mg(mg),Fe(mg),Zn(mg),P(mg),VitaminA(IU),
VitaminE(mg),VitaminB_group, VitaminC(mg),Fatty_acid_S(mg),Fatty_acid_M(mg),
Fatty_acid_P(mg),Cholesterol(mg)]
'''

nuNeed = pd.DataFrame([1918.0, 1350.0, 49.5, 191.8, 1112.4, 27, 2400, 4700, 1000, 320, 15, 12, 800, 500, 12, 20.59, 100, 300])
nuEat = pd.DataFrame([800,250,12,33,124,1,901,2300,243,123,2,3,321,123,4,7,43,126])
leftNu = np.array(nuNeed)-np.array(nuEat)
# print(leftNu)


#總體的統計
def rowData(path):
    data = pd.read_csv(path)
    dataS = data.iloc[:,[4,5,6,8,10,11,12,13,14,15,16,17,18,19,20,21,22,27]]
    dataV = np.array(dataS)
    Mean = np.mean(dataV,axis=0)
    Sigma = np.std(dataV, axis=0)
#     Value = (dataV-Mean)/Sigma
    return Mean, Sigma


# 個體依據總體統計做標準化
def standardizationt(path, all_mean, all_sigma):
    data = pd.read_csv(path)
    dataS = data.iloc[:,[3,4,5,7,9,10,11,12,13,14,15,16,17,18,19,20,21,26]]
    dataV = np.array(dataS)
#     Mean = np.mean(dataV,axis=0)
#     Sigma = np.std(dataV, axis=0)
    Value = (dataV-all_mean)/all_sigma
    return Value


# 剩餘營養素的相似度
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
    minED = min(ED_dict.keys())
    clusterED = ED_dict[minED].split('|')[0]

    # Manhattan Distance #####
    MD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        MD = pdist(X, 'cityblock')
        md = eachDishV.tolist()
        MD_dict[str(MD).strip('[').strip(']')] = f'{i}|{md}'
        i += 1
    minMD = min(MD_dict.keys())
    clusterMD = MD_dict[minMD].split('|')[0]

    # Chebyshev Distance #####
    CheD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        CheD = pdist(X, 'chebyshev')
        ched = eachDishV.tolist()
        CheD_dict[str(CheD).strip('[').strip(']')] = f'{i}|{ched}'
        i += 1
    minCheD = min(CheD_dict.keys())
    clusterCheD = CheD_dict[minCheD].split('|')[0]

    # Minkowski Distance #####
    MinkD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        MinkD = pdist(X, 'minkowski')
        minkd = eachDishV.tolist()
        MinkD_dict[str(MinkD).strip('[').strip(']')] = f'{i}|{minkd}'
        i += 1
    minMinkD = min(MinkD_dict.keys())
    clusterMinkD = MinkD_dict[minMinkD].split('|')[0]

    # Cosine Distance #####
    CosD_dict = dict()
    i = 1
    for eachDishV in dishV:
        X = np.vstack([userLeft, eachDishV])
        CosD = pdist(X, 'cosine')
        cosd = eachDishV.tolist()
        CosD_dict[str(CosD).strip('[').strip(']')] = f'{i}|{cosd}'
        i += 1
    minCosD = min(CosD_dict.keys())
    clusterCosD = CosD_dict[minCosD].split('|')[0]

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



if __name__ == '__main__':
    time_point1 = time.time()
    # 算出總體的mean和sigma
    dish = rowData(path0)
    all_mean = dish[0]
    all_sigma = dish[1]
    aa = all_mean.tolist()
    bb = all_sigma.tolist()
    A = pd.DataFrame(aa)
    B = pd.DataFrame(bb)
    # print(type(all_mean))
    # print(type(all_sigma))
    A.to_csv('totalMean.csv')
    B.to_csv('totalSigma.csv')

    # 將每一道菜做標準化（依群）
    dish1 = standardizationt(path1,all_mean,all_sigma)
    dish2 = standardizationt(path2,all_mean,all_sigma)
    dish3 = standardizationt(path3,all_mean,all_sigma)
    dish4 = standardizationt(path4,all_mean,all_sigma)
    dish5 = standardizationt(path5,all_mean,all_sigma)
    dish6 = standardizationt(path6,all_mean,all_sigma)
    dish7 = standardizationt(path7,all_mean,all_sigma)
    # 求取每一群的代表向量
    dish1V = np.mean(dish1,axis=0)
    dish2V = np.mean(dish2,axis=0)
    dish3V = np.mean(dish3,axis=0)
    dish4V = np.mean(dish4,axis=0)
    dish5V = np.mean(dish5,axis=0)
    dish6V = np.mean(dish6,axis=0)
    dish7V = np.mean(dish7,axis=0)
    dishV = np.vstack([dish1V,dish2V,dish3V,dish4V,dish5V,dish6V,dish7V])
    VV = dishV.tolist()
    V = pd.DataFrame(VV)
    V.to_csv('dish7clustersV.csv')

    # 將user剩餘的營養需求做標準化（用總體的統計資料）
    userLeftS = (leftNu.T-all_mean)/all_sigma

    # 將使用者剩餘的營養需求向量和7個菜餚群做相似度分析
    cluster = distance2(userLeftS, dishV)
    time_point2 = time.time()
    print(cluster)
    print(time_point2-time_point1)




