#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install pandas')


# In[2]:


import pandas as pd


# In[3]:


sex = []
age=[]
bmi = []
height=[]
weight=[]
cal=[]
moi=[]
pro=[]
sf=[]
car=[]
dif=[]
na=[]
k=[]
ca=[]
mg=[]
fe=[]
zn=[]
p=[]
va=[]
ve=[]
vb=[]
vc=[]
fs=[]
fm=[]
fp=[]
chol=[]


# In[4]:


people = {
    "Sex":sex,
    "Age":age,
    "Height":height,
    "Weight":weight,
    "BMI":bmi,
    "Calories":cal,
    "Moisture":moi,
    "Protein":pro,
    "Saturated_fat":sf,
    "Carbohydrate":car,
    "Dietary_fiber":dif,
    "Na":na,
    "K":k,
    "Ca":ca,
    "Mg":mg,
    "Fe":fe,
    "Zn":zn,
    "P":p,
    "VitaminA":va,
    "VitaminE":ve,
    "VitaminB_group":vb,
    "VitaminC":vc,
    "Fatty_acid_S":fs,
    "Fatty_acid_M":fm,
    "Fatty_acid_P":fp,
    "Cholesterol":chol    
}


# In[5]:


# # 安靜代謝率
# RMR = 23.1811+2.2589*SEX-0.01807*AGE-0.1448*WEIGHT+0.03797*HEIGHT
# # 安靜代謝消耗熱量
# REE = RMR*WEIGHT
# # 睡眠消耗熱量
# SEE = REE*0.9
# # 常人熱量需求
# TEE = REE + SEE
# # 過胖熱量需求

# #BMI
# BMI = WEIGHT/[(HEIGHT/100)**2]


# In[6]:


for t in range(2):   # sexQ
    for i in range(57):   # yearsQ
        for j in range(20):   #bmiQ
            for l in range(40):   #heightQ
                # SEX --------------------------------------------------------------------------------
                sex.append(t) 
                # AGE --------------------------------------------------------------------------------
                a = 19 + i
                age.append(a) 
                # BMI --------------------------------------------------------------------------------
                b = 16+j
                bmi.append(b) 
                # HEIGHT -----------------------------------------------------------------------------
                h = 140+l
                height.append(h) 
                # WEIGHT -----------------------------------------------------------------------------
                w = b*(h**2)/10000
                weight.append('%.1f'%w) 
                # Calories ---------------------------------------------------------------------------
                rmr = 23.1811+2.2589*0-0.01807*a-0.1448*w+0.03797*h
                ree = rmr*w
                see = ree*0.9
                tee = ree + see
                c = tee
                if b < 30:
                    cal.append(c)
                else:
                    cal.append(c-500)
                # Moisture(體重的30倍) ----------------------------------------------------------------
                m = w *30
                moi.append(m)
                # Saturated_fat(熱量的0.1倍) ----------------------------------------------------------
                s = c * 0.1
                sf.append(s)
                # Carbohydrate(熱量的0.58倍) ----------------------------------------------------------
                carb = c * 0.58
                car.append(carb)
                # Na(相同固定值)
                na.append(2400)
                # k(相同固定值)
                k.append(4700)
                # Ca(相同固定值)
                ca.append(1000)
                # P(相同固定值)
                p.append(800)
                # VitaminE(相同固定值)
                ve.append(12)
                # VitaminC(相同固定值)
                vc.append(100)
                # Cholesterol(相同固定值)
                chol.append(300)
                # Protein(體重小於等於71kg,蛋白質為體重的1.1倍；體重大於71，蛋白質為體重的1.2倍) ------------
                pro.append(w*1.1 if a<71 else w*1.2)
                # Fatty_acid_S(熱量的0.1倍)
                fs.append(c*0.1)
                # Fatty_acid_M(熱量的0.06倍)
                fm.append(c*0.06)
                # Fatty_acid_P(熱量的0.009倍)
                fp.append(c*0.009)
                # Dietary_fiber & Zn & Mg $ Fe & VitaminA & VitaminB -----------------------------------  
                if t == 0:
                    zn.append(12)
                    va.append(500)
                    vb.append(20.59)
                    if a < 51:
                        dif.append(27)
                        mg.append(320)
                        fe.append(15)
                    elif 50<a<71:
                        dif.append(25)
                        mg.append(310)
                        fe.append(10)
                    else:
                        dif.append(24)
                        mg.append(300)
                        fe.append(10)
                else:
                    zn.append(15)
                    fe.append(10)
                    va.append(600)
                    vb.append(23.25)
                    if a < 51:
                        dif.append(34)
                        mg.append(380)
                    elif 50<a<71:
                        dif.append(32)
                        mg.append(360)
                    else:
                        dif.append(30)
                        mg.append(350)
                # 
                
            
    
df = pd.DataFrame(people)

df.to_csv('peopleSample.csv')




