import pymysql, redis


def search_dish(condition):
    # SELECT * FROM i_nutrition.chowder_recipe_nutrients_content_per100g;
    host = '35.229.172.113'
    port = 3306
    user = 'food2'
    password = '1234'
    db = 'i_nutrition'
    table = 'chowder_recipe_nutrients_content_per100g'
    # condition = condition
    print(f"Now connecting to MySQL: {host}")
    connection = pymysql.connect(host=host, port=port, db=db, user=user, passwd=password, charset="utf8")
    cursor = connection.cursor()
    print(f"Now using database: {db}")
    # sql = f"SELECT * FROM {db}.{table} WHERE 'recipe' = '{condition}';"
    sql = f"SELECT * from {table} WHERE recipe = '{condition}';"
    try:
        cursor.execute(sql)
        fetch = cursor.fetchone()
    except Exception as e:
        print(f'Something Wrong:\n\t\t\t{e}')
        return
    return fetch


def redisStore(key, value):
    r = redis.Redis(host='172.17.0.2', port=6379, decode_responses=True, password='4321')
    # key_value = f'{key},{value}'
    r.set(key, value, ex=432000, nx=True)
    print(r.get(key))
    return key, value


if __name__ == '__main__':
    try:
        recipe = search_dish('咖哩飯')
        recipe_nutrition = recipe
        dishName = recipe_nutrition[2]
        Calories = recipe_nutrition[3]
        Carbohydrate = recipe_nutrition[9]
        Protein = recipe_nutrition[5]
        Saturated_fat = recipe_nutrition[7]
        result = f'「{dishName}(/100g)」搜尋結果為：\n' \
                 f'\t熱量(kcal):{Calories}\n' \
                 f'\t碳水化合物(g):{Carbohydrate}\n' \
                 f'\t蛋白質(g):{Protein}\n' \
                 f'\t脂質(g):{Saturated_fat}\n'
        print(result)
        result_for_redis = f'{dishName}|{Calories}|{Carbohydrate}|{Protein}|{Saturated_fat}'
        redis_key = result_for_redis.split('|')[0]
        redis_value = result_for_redis.split('|')[1:]
        redisStore(redis_key, redis_value)

    except Exception as e:
        print('未收錄此道菜名，請換個名字或搜尋其他菜餚。')
        print(e)
