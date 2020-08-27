import pandas as pd
import re

# columnName=["Sex","Age","Hight","Weight","Calories","Moisture","Protein","saturated_fat","Carbohydrate","Dietary_fiber","Na","K","Ca","Mg","Fe","Zn","P","VitaminA","VitaminE","VitaminB_group","VitaminC", "Fatty_acid_S","Fatty_acid_M","Fatty_acid_P","Cholesterol"]

# for c in columnName:
#     print(c)

sex = []
age = []
peopleSample = {
    "Sex": sex,
    "Age": age,
    "Height": [],
    "Weight": [],
    "Clories": [],
    "Moisture":[],
    "Protein":[],
    "saturated_fat":[],
    "Carbohydrate":[],
    "Dietary_fiber":[],
    "Na":[],
    "K":[],
    "Ca":[],
    "Mg":[],
    "Fe":[],
    "Zn":[],
    "P":[],
    "VitaminA":[],
    "VitaminE":[],
    "VitaminB_group":[],
    "VitaminC":[],
    "Fatty_acid_S":[],
    "Fatty_acid_M":[],
    "Fatty_acid_P":[],
    "Cholesterol":[]
}

df = pd.DataFrame(peopleSample)

# print(df)

#years:19-75;BMI:16-35;Height:150-190
for i in range(45600):
    sex.append(0 if i < 45600 else 1)

print(df)
    # t = 1
    # range_1, range_2 = 800*(t-1), 800*t
    # if i in range(range_1,range_2):
    #     peopleSample["Age"].append(19*t)
    #     t += 1
    #
    # peopleSample["Height"].append('0')
    # peopleSample["Weight"].append('0')
    # peopleSample["Clories"].append('0')
    # peopleSample["Moisture"].append('0')
    # peopleSample["Protein"].append('0')
    # peopleSample["saturated_fat"].append('0')
    # peopleSample["Carbohydrate"].append('0')
    # peopleSample["Dietary_fiber"].append('0')
    # peopleSample["Na"].append('0')
    # peopleSample["K"].append('0')
    # peopleSample["Ca"].append('0')
    # peopleSample["Mg"].append('0')
    # peopleSample["Fe"].append('0')
    # peopleSample["Zn"].append('0')
    # peopleSample["P"].append('0')
    # peopleSample["VitaminA"].append('0')
    # peopleSample["VitaminE"].append('0')
    # peopleSample["VitaminB_group"].append('0')
    # peopleSample["VitaminC"].append('0')
    # peopleSample["Fatty_acid_S"].append('0')
    # peopleSample["Fatty_acid_M"].append('0')
    # peopleSample["Fatty_acid_P"].append('0')
    # peopleSample["Cholesterol"].append('0')
