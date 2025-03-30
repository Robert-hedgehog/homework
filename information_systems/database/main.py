import sqlite3

connection = sqlite3.connect("baza.db")
cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS `job_titles` (
	    `id_job_title` integer primary key NOT NULL UNIQUE,
	    `name` TEXT NOT NULL
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS `employees` (
        `id` integer primary key NOT NULL UNIQUE,
        `surname` TEXT NOT NULL,
        `name` TEXT NOT NULL,
        `id_job_title` INTEGER NOT NULL,
    FOREIGN KEY(`id_job_title`) REFERENCES `job_titles`(`id_job_title`)
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS `orders` (
        `id_order` integer primary key NOT NULL UNIQUE,
        `id_client` INTEGER NOT NULL,
        `id_job_title` INTEGER NOT NULL,
        `sum` INTEGER NOT NULL,
        `data` DATETIME NOT NULL,
        `check_mark` BOOLEAN NOT NULL,
    FOREIGN KEY(`id_client`) REFERENCES `clients`(`id_client`),
    FOREIGN KEY(`id_job_title`) REFERENCES `employees`(`id_job_title`)
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS `clients` (
        `id_client` integer primary key NOT NULL UNIQUE,
        `organization` TEXT NOT NULL,
        `phone` INTEGER NOT NULL
    );
''')
job_titles_data = [
    (1, "Менеджер"),
    (2, "Разработчик"),
    (3, "Аналитик"),
    (4, "Дизайнер"),
]
cursor.executemany("INSERT OR IGNORE INTO 'job_titles' ('id_job_title', 'name') VALUES (?, ?)", job_titles_data)
employees_data = [
    (1, "Иванов", "Иван", 2),
    (2, "Петров", "Петр", 1),
    (3, "Сидорова", "Мария", 3),
    (4, "Козлов", "Алексей", 2),
    (5, "Васильева", "Ольга", 4),
    (6, "Каримова", "Мария", 1),
    (7, "Белов", "Олег", 4)
]
cursor.executemany("INSERT OR IGNORE INTO 'employees' ('id', 'surname', 'name', 'id_job_title') VALUES (?, ?, ?, ?)", employees_data)
orders_data = [
    (1, 3, 1, 155000, '15-07-2023', True),  
    (2, 4, 2, 545455, '22-11-2018', True), 
    (3, 2, 3, 46460, '28-04-2024', True),
    (4, 1, 4, 898654, '12-03-2010', True), 
    (5, 1, 3, 546544, '02-03-2010', True)
]
cursor.executemany("INSERT OR IGNORE INTO 'orders' ('id_order', 'id_client', 'id_job_title', 'sum', 'data', 'check_mark') VALUES (?, ?, ?, ?, ?, ?)", orders_data)
clients_data = [
    (1, 'ООО "Быстрая Доставка"', '89101234567'),  
    (2, 'ООО "ТехноРемонт"', '89507778899'),  
    (3, 'ООО "Мастер на все руки"', '88765432100'),
    (4, 'ООО "Все под рукой"', "89201452678") 
]
cursor.executemany("INSERT OR IGNORE INTO 'clients' ('id_client', 'organization', 'phone') VALUES (?, ?, ?)", clients_data)

connection.commit()

cursor.execute("""
    SELECT COUNT(*) FROM employees;
""")
count_employees = cursor.fetchone()[0]
print(f"Количество сотрудников: {count_employees}")

cursor.execute("""
    SELECT MAX(sum) FROM orders;
""")
max_order_sum = cursor.fetchone()[0]
print(f"Максимальная сумма заказа: {max_order_sum}")

cursor.execute("""
    SELECT SUM(sum) FROM orders;
""")
total_order_sum = cursor.fetchone()[0]
print(f"Суммарная стоимость всех заказов: {total_order_sum}")

cursor.execute("""
    SELECT AVG(sum) FROM orders;
""")
sr_order_sum = cursor.fetchone()[0]
print(f"Средняя стоимость заказа: {sr_order_sum}")

cursor.execute("""
    SELECT COUNT(*) FROM clients;
""")
count_clients = cursor.fetchone()[0]
print(f"Количество клиентов: {count_clients}")

cursor.execute("""
    SELECT job_titles.name, COUNT(*) AS total_employees
    FROM employees
    JOIN job_titles ON employees.id_job_title = job_titles.id_job_title
    GROUP BY job_titles.name;
""")
job_title_counts = cursor.fetchall()
print("\nКоличество сотрудников по должностям:")
for job_title in job_title_counts:
    print(job_title)

cursor.execute("""
    SELECT job_titles.name, AVG(orders.sum) AS avg_order_sum
    FROM orders
    JOIN employees ON orders.id_job_title = employees.id_job_title
    JOIN job_titles ON employees.id_job_title = job_titles.id_job_title
    GROUP BY job_titles.name;
""")
sr_by_job = cursor.fetchall()
print("\nСредняя сумма заказа по должностям:")
for job in sr_by_job:
    print(job)

cursor.execute("""
    SELECT job_titles.name, COUNT(*)
    FROM employees
    JOIN job_titles ON employees.id_job_title = job_titles.id_job_title
    GROUP BY employees.id_job_title
    HAVING COUNT(*) > 1;
""")
job_titles_more_than_one = cursor.fetchall()
print("\nДолжности, где количество сотрудников больше 1:")
for job in job_titles_more_than_one:
    print(job)
    
cursor.execute("""
    SELECT orders.id_order, clients.organization, orders.sum
    FROM orders
    JOIN clients ON orders.id_client = clients.id_client;
""")
order_list = cursor.fetchall()
print("\nСписок заказов с данными о клиентах:")
for order in order_list:
    print(order)

cursor.execute("""
    SELECT employees.surname, employees.name, job_titles.name AS job_title
    FROM employees
    JOIN job_titles ON employees.id_job_title = job_titles.id_job_title;
""")
employee_list = cursor.fetchall()
print("\nСписок сотрудников и их должностей:")
for employee in employee_list:
    print(employee)

cursor.execute("""
    SELECT orders.id_order, clients.organization, orders.sum, orders.data
    FROM orders
    JOIN clients ON orders.id_client = clients.id_client
    WHERE orders.data > '2020-01-01';
""")
recent_orders = cursor.fetchall()
print("\nЗаказы, выполненные после 2020 года:")
for order in recent_orders:
    print(order)

connection.close()