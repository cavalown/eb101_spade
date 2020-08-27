'''
1. get user input basic information from SQL
2. compute user's every nutrition need and Cluster
3. need of nutrition store to SQL
4. first recommend with Cluster store to kafka (topic: Dish_recommend)
'''

import pandas as pd
import numpy as np
import datetime
import time
import random
from scipy.spatial.distance import pdist
from MyPackages.connect import connectMySQL


##### 基礎每日營養需求換算 #####
class UserNeedNu:
    ### 固定值的初始營養素
    def __init__(self):
        self.na = 2400
        self.k = 4700
        self.ca = 1000
        self.p = 800
        self.ve = 12
        self.vc = 100
        self.chol = 300

    #### 根據基本資料換算成營養素需求
    def userBasic(self, X):
        ## info:
        self.sex = int(X[0])
        self.birthstr = str(X[1])
        self.height = float(X[2])
        self.weight = float(X[3])
        self.goal = X[-1][-1]

        today = datetime.datetime.today()
        birth = datetime.datetime.strptime(self.birthstr, '%Y%m%d')
        age = int(((today - birth).days) / 365)
        bmi = round(self.weight / float((self.height / 100) ** 2), 1)

        ## nutrition need:
        # (na,k,ca,p,ve,vc,chol) = (2400, 4700, 1000, 800, 12, 100, 300)
        cal = round((
                            23.1811 + 2.2589 * self.sex - 0.01807 * age - 0.1448 * self.weight + 0.03797 * self.height) * 1.9 * self.weight,
                    1)
        moi = round(self.weight * 30, 1)
        pro = (round(self.weight * 1.1, 1) if age < 71 else round(self.weight * 1.2, 1))
        sf = round(cal * 0.1, 1)
        car = round(cal * 0.58, 1)
        fs = round(cal * 0.1, 1)
        fm = round(cal * 0.06, 1)
        fp = round(cal * 0.009, 1)

        ## sex leads nutrition
        if self.sex == 0:
            (zn, va, vb) = (12, 500, 20.59)
            if age < 51:
                (dif, mg, fe) = (27, 320, 15)
            elif 50 < age < 71:
                (dif, mg, fe) = (25, 310, 10)
            else:
                (dif, mg, fe) = (24, 300, 10)
        else:
            (zn, va, vb, fe) = (15, 600, 23.25, 10)
            if age < 51:
                (dif, mg) = (34, 300)
            elif 50 < age < 71:
                (dif, mg) = (32, 360)
            else:
                (dif, mg) = (30, 350)
        ## goal leads nutrition
        ### goal 1: normal
        ### goal 2: lose weight
        if self.goal == 2:
            car = round(car * 0.34, 2)
            pro = round(pro * 1.67, 2)
            sf = round(sf * 2, 2)
        ### goal 3: increase weight
        elif self.goal == 3:
            cal = round(cal * 1.5, 2)
            car = round(car * 1.5 * 0.95, 2)
            pro = round(pro * 1.5 * 1.39, 2)
            sf = round(sf * 1.5 * 0.8, 2)
            fs = round(fs * 1.5, 2)
            fm = round(fm * 1.5, 2)
            fp = round(fp * 1.5, 2)
        ### goal 4: increase muscle
        elif self.goal == 4:
            cal = round(cal * 1.2, 2)
            car = round(car * 1.2 * 0.95, 2)
            pro = round(pro * 1.2 * 1.39, 2)
            sf = round(sf * 1.2 * 0.8, 2)
            fs = round(fs * 1.2, 2)
            fm = round(fm * 1.2, 2)
            fp = round(fp * 1.2, 2)
        ### goal 5: ketogenic diet
        elif self.goal == 5:
            car = round(car * 0.09, 2)
            pro = round(pro * 1.11, 2)
            sf = round(sf * 3, 2)

        self.userNu = [self.sex, age, bmi, self.height, self.weight, cal, moi, pro, sf, car, dif, self.na, self.k,
                       self.ca, \
                       mg, fe, zn, self.p, va, self.ve, vb, self.vc, fs, fm, fp, self.chol]
        # self.userNu = np.array(self.userNu)
        return self.userNu


##### 相似度分析 並推薦餐 #####
class FirstRecommend:
    # def __init__(self):

    # Eucledian Distance
    def euDis(self, sample, data):
        self.sample = sample
        self.userNu = data
        sampleV = np.array(self.sample)
        userNuV = np.array(self.userNu)
        minED = [100000000000]
        content1 = []
        for eachSample in sampleV:
            # print(eachSample)
            X = np.vstack([userNuV, eachSample[:-1]])
            ED = pdist(X)
            if ED < minED[0]:
                minED = ED
                content1 = eachSample

        print('E Distance:\n', minED[0])
        print('Sample content:\n', content1)
        cluster = self.sample[self.sample.Sex == content1[0]][self.sample.Age == content1[1]][self.userNu.Height == content1[2]][
            self.sample.BMI == content1[4]].Cluster
        print('Cluster:\n',cluster)
        userCluster_e = cluster.iloc[0]
        print(userCluster_e)
        print('-' * 20)


if __name__ == '__main__':
    # 連線MySQL取出User輸入的基本資料
    a = connectMySQL.SQLconnect()
    a.sqlConnection()
    user_input = a.search_item('*', 'i_member.member')[0]
    user_inBas = list(user_input)[2:7]

    # 換算User需求的Nutrition，並存入MySQL
    user_nu = UserNeedNu().userBasic(user_inBas)
    # print(user_nu)
    # b = connectMySQL.SQLconnect(db='testt')
    # b.sqlConnection()
    # sss = 'NULL'
    #
    # for ii in user_nu:
    #     sss += ',' + str(ii)
    #
    # value = sss
    # b.insert('testt.memberNuNeed', value)

    # 把Nutrition Need進行相似度分析
    # 1.先把Sample準備好
    Sample = pd.read_csv('peopleSample_cluster.csv', index_col='X')
    sampleData = Sample.iloc[:, 1:]
    # print(sampleData)
    # user_nuData = np.array(user_nu)
    # print(user_nuData)
    # 2.
    b = FirstRecommend()
    b.euDis(sampleData,user_nu)