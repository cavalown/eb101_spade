import json


dic={"商家名稱": "井格老灶火鍋(望京新世界店)", "評分": 26.2, "地址": "火鍋望京廣順南大街路16號", "人均消費": 105, "評論數量": 1387}
with open('tt.json','a',newline='') as outfile:
    json.dump(dic,outfile,ensure_ascii=False)
    outfile.write('\n')