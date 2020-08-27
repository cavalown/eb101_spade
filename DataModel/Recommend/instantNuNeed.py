import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

Need = [1000] * 6
# print(Need)
First = [200, 300] * 3
print(First)

Left = pd.Series(Need) - pd.Series(First)
# Need - First


wsterN = Need[0]
waterD = First[0]
waterL = wsterN - waterD

plt.figure(figsize=(6, 9))  # 顯示圖框架大小

labels = "Need of Water"  # 製作圓餅圖的類別標籤
separeted = (500, 1000, 1500, 2000, 2500)  # 依據類別數量，分別設定要突出的區塊
size = [waterL, waterD]  # 製作圓餅圖的數值來源

plt.pie(size,  # 數值
        labels=labels,  # 標籤
        autopct="%1.1f%%",  # 將數值百分比並留到小數點一位
        explode=separeted,  # 設定分隔的區塊位置
        pctdistance=0.6,  # 數字距圓心的距離
        textprops={"fontsize": 12},  # 文字大小
        shadow=True)  # 設定陰影

plt.axis('equal')  # 使圓餅圖比例相等
plt.title("Pie chart of car accident", {"fontsize": 18})  # 設定標題及其文字大小
plt.legend(loc="best")  # 設定圖例及其位置為最佳

plt.savefig("Pie chart of car accident.jpg",  # 儲存圖檔
            bbox_inches='tight',  # 去除座標軸占用的空間
            pad_inches=0.0)  # 去除所有白邊
plt.close()  # 關閉圖表
