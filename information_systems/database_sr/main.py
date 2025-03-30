
# Используя информацию из приведённой базы данных, определите, магазины какого района получили наибольшую выручку от продажи товаров отдела «Молоко».

# Ответ: 38424422


import sqlite3

connection = sqlite3.connect("baza.db")
cursor = connection.cursor()

for s in open("shop.txt"):
    shop = s.strip().split()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `shop` (
            `id_shop` TEXT primary key NOT NULL UNIQUE,
            `district` TEXT NOT NULL
        ); 
    ''')

    cursor.execute("INSERT INTO shop VALUES (?, ?)", (shop[0], shop[1]))

for s2 in open("product.txt"):
    product = s2.strip().split()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `product` (
            `article` integer primary key NOT NULL UNIQUE,
            `department` TEXT NOT NULL,
            `name_pr` TEXT NOT NULL,
            `unit of measurement` TEXT NOT NULL,
            `quantity` FLOAT NOT NULL,
            `supplier` TEXT NOT NULL
        );
    ''')

    cursor.execute("INSERT INTO product VALUES (?, ?, ?, ?, ?, ?)", (product[0], product[1], product[2], product[3], product[4], product[5]))

for s3 in open("trade.txt"):
    trade = s3.strip().split()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS `trade` (
            `id_operations` integer primary key NOT NULL UNIQUE,
            `date` TEXT NOT NULL,
            `shop` TEXT NOT NULL,
            `article` INTEGER NOT NULL,
            `operation` TEXT NOT NULL,
            `number_of_packages` INTEGER NOT NULL,
            `price` INTEGER NOT NULL,
        FOREIGN KEY(`shop`) REFERENCES `shop`(`id_shop`),
        FOREIGN KEY(`article`) REFERENCES `product`(`article`)
        );
    ''')

    cursor.execute("INSERT INTO trade VALUES (?, ?, ?, ?, ?, ?, ?)", (trade[0], trade[1], trade[2], trade[3], trade[4], trade[5], trade[6]))

connection.commit()

cursor.execute('''
    SELECT shop.district, SUM(trade.number_of_packages * trade.price) AS total_revenue
    FROM trade
    JOIN product ON trade.article = product.article
    JOIN shop ON trade.shop = shop.id_shop
    WHERE product.department = 'Молоко' AND trade.operation = 'Продажа'
    GROUP BY shop.district
    ORDER BY total_revenue DESC
    LIMIT 1;
''')

result = cursor.fetchone()

if result:
    print(f"Выручка: {result[1]}")
else:
    print("Нет данных по продажам молочной продукции.")

connection.close()