import csv

with open('cookpadFC.csv', newline='') as f:
    rows = csv.reader(f, delimiter=',')
    for row in rows:
        column = row[2]
        # print(column)
        column=column.replace('[','').replace(']','').replace("'",'')
        print(type(column))

        name = row[0]
        ingredient = column
        recipeUrl = row[1]
        picUrl = row[3]

        # with open('cookpad.csv','a',encoding='utf-8',newline='') as csvfile:
        #     csvWriter = csv.writer(csvfile)
        #     csvWriter.writerow([name,ingredient,recipeUrl,picUrl])

        with open('cookpading.csv','a',encoding='utf-8',newline='') as csvfile:
            csvWriter = csv.writer(csvfile)
            csvWriter.writerow([ingredient])


