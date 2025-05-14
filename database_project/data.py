import sqlite3
from datetime import datetime, timedelta
import random

def connect_db():
    return sqlite3.connect('pharmacy.db')

def add_test_data():
    conn = connect_db()
    cursor = conn.cursor()
    today = datetime.now().date()

    # 1. Поставщики (25 записей)
    suppliers = [
        ("Фармакор", "contact@pharmakor.ru", "1234567890", "123456789"),
        ("Аптечная сеть 'Здоровье'", "info@zdorovie.ru", "0987654321", "987654321"),
        ("БиоФарм", "sales@biofarm.com", "1122334455", "112233445"),
        ("Фармстандарт", "order@pharmstd.ru", "5566778899", "556677889"),
        ("Вертекс", "supply@vertex.ru", "3344556677", "334455667"),
        ("Обновление", "sales@obnovlenie.ru", "9988776655", "998877665"),
        ("Синтез", "info@syntez.ru", "1123581321", "112358132"),
        ("Фармапол", "order@pharmapol.ru", "3141592653", "314159265"),
        ("Биотех", "supply@biotech.ru", "2718281828", "271828182"),
        ("Дальхимфарм", "sales@dhf.ru", "1618033988", "161803398"),
        ("Ниармедик", "info@niarmedik.ru", "1414213562", "141421356"),
        ("Эвалар", "order@evar.ru", "5772156649", "577215664"),
        ("Брынцалов", "supply@bryntsalov.ru", "6626070046", "662607004"),
        ("Макиз-Фарма", "sales@makiz.ru", "7241275950", "724127595"),
        ("Мосхимфарм", "info@moschim.ru", "1353018524", "135301852"),
        ("Татхимфарм", "order@tatpharm.ru", "1570796326", "157079632"),
        ("Фармасинтез", "supply@pharmas.ru", "3141592653", "314159265"),
        ("Биохимик", "sales@biochem.ru", "5772156649", "577215664"),
        ("Велфарм", "info@velpharm.ru", "6626070046", "662607004"),
        ("Гедеон Рихтер", "order@richter.ru", "7241275950", "724127595"),
        ("КРКА", "supply@krka.ru", "1353018524", "135301852"),
        ("Новартис", "sales@novartis.ru", "1570796326", "157079632"),
        ("Пфайзер", "info@pfizer.ru", "3141592653", "314159265"),
        ("Санофи", "order@sanofi.ru", "5772156649", "577215664"),
        ("Байер", "supply@bayer.ru", "6626070046", "662607004")
    ]
    cursor.executemany(
        "INSERT INTO Поставщики (Наименование, Контакты, ИНН, КПП) VALUES (?, ?, ?, ?)",
        suppliers
    )

    # 2. Сотрудники (20 записей)
    employees = [
        ("Кузнецова Елена Владимировна", "Заведующая", "+79031234567", "kuznetsova@pharmacy.ru"),
        ("Лебедев Максим Александрович", "Менеджер", "+79167890123", "lebedev@pharmacy.ru"),
        ("Алексеев Павел Дмитриевич", "Менеджер", "+79164567890", "alekseev@pharmacy.ru"),
        ("Иванова Анна Петровна", "Провизор", "+79161234567", "ivanova@pharmacy.ru"),
        ("Сидорова Ольга Николаевна", "Провизор", "+79036789012", "sidorova@pharmacy.ru"),
        ("Федорова Екатерина Игоревна", "Провизор", "+79038901234", "fedorova@pharmacy.ru"),
        ("Морозова Анастасия Дмитриевна", "Провизор", "+79032345678", "morozova@pharmacy.ru"),
        ("Козлова Ирина Викторовна", "Провизор", "+79030123456", "kozlova@pharmacy.ru"),
        ("Смирнов Дмитрий Игоревич", "Фармацевт", "+79035678901", "smirnov@pharmacy.ru"),
        ("Петров Сергей Александрович", "Фармацевт", "+79162345678", "petrov@pharmacy.ru"),
        ("Николаева Марина Сергеевна", "Фармацевт", "+79037890123", "nikolaeva@pharmacy.ru"),
        ("Григорьев Артем Валерьевич", "Фармацевт", "+79165678901", "grigoriev@pharmacy.ru"),
        ("Дмитриев Андрей Сергеевич", "Фармацевт", "+79166789012", "dmitriev@pharmacy.ru"),
        ("Соколова Виктория Олеговна", "Фармацевт", "+79031234567", "sokolova@pharmacy.ru"),
        ("Волков Роман Сергеевич", "Фармацевт", "+79169012345", "volkov@pharmacy.ru"),
        ("Андреева Юлия Андреевна", "Фармацевт", "+79033456789", "andreeva@pharmacy.ru"),
        ("Васильев Игорь Викторович", "Кассир", "+79163456789", "vasiliev@pharmacy.ru"),
        ("Борисова Наталья Петровна", "Кассир", "+79039012345", "borisova@pharmacy.ru"),
        ("Павлов Денис Игоревич", "Кассир", "+79168901234", "pavlov@pharmacy.ru"),
        ("Тихонов Алексей Викторович", "Кассир", "+79160123456", "tikhonov@pharmacy.ru")
    ]
    cursor.executemany(
        "INSERT INTO Сотрудники (ФИО, Должность, Телефон, Email) VALUES (?, ?, ?, ?)",
        employees
    )

    # 3. Клиенты (30 записей)
    clients = [
        ("Петров Алексей Сергеевич", "+79167778899", "CARD001"),
        ("Соколова Мария Ивановна", "+79039998877", "CARD002"),
        ("Васильев Игорь Николаевич", "+79168887766", "CARD003"),
        ("Ковалева Анна Дмитриевна", "+79037776655", "CARD004"),
        ("Никитин Сергей Владимирович", "+79169995544", "CARD005"),
        ("Морозова Елена Александровна", "+79036664433", "CARD006"),
        ("Григорьев Павел Игоревич", "+79161112233", "CARD007"),
        ("Орлова Ольга Сергеевна", "+79035553344", "CARD008"),
        ("Белов Дмитрий Анатольевич", "+79162223344", "CARD009"),
        ("Зайцева Наталья Викторовна", "+79034445566", "CARD010"),
        ("Крылов Артем Олегович", "+79163334455", "CARD011"),
        ("Полякова Ирина Петровна", "+79033336677", "CARD012"),
        ("Медведев Андрей Николаевич", "+79164445566", "CARD013"),
        ("Фролова Татьяна Владимировна", "+79032227788", "CARD014"),
        ("Семенов Иван Дмитриевич", "+79165556677", "CARD015"),
        ("Антонова Екатерина Сергеевна", "+79031118899", "CARD016"),
        ("Тарасов Виктор Петрович", "+79166667788", "CARD017"),
        ("Беляева Марина Андреевна", "+79030009988", "CARD018"),
        ("Данилов Алексей Игоревич", "+79167778899", "CARD019"),
        ("Кузьмина Вероника Олеговна", "+79038997766", "CARD020"),
        ("Лазарев Денис Викторович", "+79168889900", None),
        ("Сорокина Алина Дмитриевна", "+79037770011", None),
        ("Титов Роман Сергеевич", "+79169990022", None),
        ("Устинова Юлия Андреевна", "+79036661133", None),
        ("Федотов Артем Игоревич", "+79161113344", None),
        ("Харитонова Надежда Петровна", "+79035554466", None),
        ("Цветков Владислав Олегович", "+79162224455", None),
        ("Чернова Ангелина Сергеевна", "+79034446677", None),
        ("Шестаков Михаил Дмитриевич", "+79163335566", None),
        ("Щербакова Виктория Андреевна", "+79032228899", None)
    ]
    cursor.executemany(
        "INSERT INTO Клиенты (ФИО, Телефон, Номер_карты_лояльности) VALUES (?, ?, ?)",
        clients
    )

    # 4. Товары (30 записей)
    products = [
        ("Парацетамол 500мг таб. №20", "Жаропонижающие", "Фармстандарт", "Таблетки", "500мг", 0, 85.50),
        ("Ибупрофен 200мг таб. №30", "Обезболивающие", "Биохимик", "Таблетки", "200мг", 0, 120.00),
        ("Амоксициллин 500мг капс. №16", "Антибиотики", "Синтез", "Капсулы", "500мг", 1, 150.75),
        ("Називин 0.05% капли 10мл", "Сосудосуживающие", "Bayer", "Капли", "0.05%", 0, 210.00),
        ("Нурофен Экспресс 400мг капс. №12", "Обезболивающие", "Reckitt Benckiser", "Капсулы", "400мг", 0, 250.50),
        ("Активированный уголь таб. №10", "Энтеросорбенты", "Фармстандарт", "Таблетки", "250мг", 0, 35.20),
        ("Лоперамид 2мг капс. №10", "Противодиарейные", "Обновление", "Капсулы", "2мг", 0, 45.80),
        ("Аспирин 500мг таб. №20", "Жаропонижающие", "Bayer", "Таблетки", "500мг", 0, 95.30),
        ("Супрастин 25мг таб. №20", "Антигистаминные", "Эгис", "Таблетки", "25мг", 0, 120.75),
        ("Мезим форте таб. №20", "Ферменты", "Берлин-Хеми", "Таблетки", "10000ЕД", 0, 85.90),
        ("Глицин 100мг таб. №50", "Неврологические", "Биотики", "Таблетки", "100мг", 0, 65.40),
        ("Валерьянка таб. №50", "Седативные", "Фармстандарт", "Таблетки", "20мг", 0, 55.25),
        ("Кагоцел таб. №10", "Противовирусные", "Ниармедик", "Таблетки", "12мг", 0, 240.60),
        ("Арбидол 100мг капс. №10", "Противовирусные", "Фармстандарт", "Капсулы", "100мг", 0, 320.00),
        ("Омепразол 20мг капс. №30", "Гастроэнтерологические", "Обновление", "Капсулы", "20мг", 0, 95.80),
        ("Кларитин 10мг таб. №10", "Антигистаминные", "Bayer", "Таблетки", "10мг", 0, 180.40),
        ("Фенистил гель 30г", "Антигистаминные", "Новартис", "Гель", "0.1%", 0, 420.50),
        ("Мирамистин р-р 50мл", "Антисептики", "Инфамед", "Раствор", "0.01%", 0, 280.75),
        ("Хлоргексидин 0.05% р-р 100мл", "Антисептики", "Обновление", "Раствор", "0.05%", 0, 45.90),
        ("Бепантен крем 30г", "Дерматологические", "Bayer", "Крем", "5%", 0, 520.00),
        ("Пантенол спрей 130г", "Дерматологические", "Фармстандарт", "Спрей", "4.63%", 0, 380.25),
        ("Анальгин 500мг таб. №10", "Обезболивающие", "Фармстандарт", "Таблетки", "500мг", 0, 45.60),
        ("Цитрамон П таб. №10", "Обезболивающие", "Фармстандарт", "Таблетки", "Комплекс", 0, 65.30),
        ("Валидол таб. №10", "Сердечно-сосудистые", "Фармстандарт", "Таблетки", "60мг", 0, 35.90),
        ("Корвалол капли 25мл", "Сердечно-сосудистые", "Фармстандарт", "Капли", "Комплекс", 0, 95.40),
        ("Амбробене сироп 100мл", "Отхаркивающие", "Меркле", "Сироп", "15мг/5мл", 0, 120.80),
        ("Лазолван таб. №20", "Отхаркивающие", "Берингер Ингельхайм", "Таблетки", "30мг", 0, 240.50),
        ("Смекта пак. №10", "Гастроэнтерологические", "Бофур Ипсен", "Порошок", "3г", 0, 150.75),
        ("Линекс капс. №16", "Пробиотики", "Лек", "Капсулы", "Комплекс", 0, 320.00),
        ("Эссенциале форте Н капс. №30", "Гепатопротекторы", "Санофи", "Капсулы", "300мг", 0, 580.60)
    ]
    cursor.executemany(
        """INSERT INTO Товары (
            Наименование, Категория, Производитель, Форма_выпуска, Дозировка, Рецептурный, Цена_розничная
        ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        products
    )

    # 5. Партии товаров (60 записей)
    batches = [
        (1, "PAR2023001", 100, 30, today + timedelta(days=90), 45.00, today - timedelta(days=10), 1),
        (1, "PAR2023002", 50, 50, today + timedelta(days=180), 42.50, today - timedelta(days=5), 2),
        (2, "IBU2023001", 80, 15, today + timedelta(days=60), 75.00, today - timedelta(days=15), 1),
        (3, "AMX2023001", 40, 40, today + timedelta(days=120), 90.00, today - timedelta(days=20), 3),
        (4, "NAZ2023001", 60, 10, today + timedelta(days=30), 120.00, today - timedelta(days=8), 2),
        (5, "NUR2023001", 30, 5, today + timedelta(days=150), 150.00, today - timedelta(days=3), 1),
        (6, "AC2023001", 200, 80, today + timedelta(days=270), 15.00, today - timedelta(days=12), 4),
        (7, "LOP2023001", 150, 45, today + timedelta(days=180), 25.00, today - timedelta(days=18), 5),
        (8, "ASP2023001", 120, 60, today + timedelta(days=240), 45.00, today - timedelta(days=7), 6),
        (9, "SUP2023001", 80, 25, today + timedelta(days=210), 60.00, today - timedelta(days=15), 7),
        (10, "MEZ2023001", 100, 40, today + timedelta(days=300), 45.00, today - timedelta(days=10), 8),
        (11, "GLY2023001", 150, 75, today + timedelta(days=360), 30.00, today - timedelta(days=5), 9),
        (12, "VAL2023001", 200, 100, today + timedelta(days=270), 25.00, today - timedelta(days=20), 10),
        (13, "KAG2023001", 50, 15, today + timedelta(days=180), 120.00, today - timedelta(days=8), 11),
        (14, "ARB2023001", 60, 20, today + timedelta(days=210), 160.00, today - timedelta(days=12), 12),
        (15, "OME2023001", 70, 30, today + timedelta(days=240), 45.00, today - timedelta(days=15), 13),
        (16, "CLA2023001", 80, 35, today + timedelta(days=270), 90.00, today - timedelta(days=7), 14),
        (17, "FEN2023001", 40, 10, today + timedelta(days=180), 210.00, today - timedelta(days=10), 15),
        (18, "MIR2023001", 60, 20, today + timedelta(days=210), 140.00, today - timedelta(days=5), 16),
        (19, "CHL2023001", 120, 50, today + timedelta(days=360), 20.00, today - timedelta(days=15), 17),
        (20, "BEP2023001", 30, 8, today + timedelta(days=180), 260.00, today - timedelta(days=8), 18),
        (21, "PAN2023001", 40, 12, today + timedelta(days=210), 190.00, today - timedelta(days=12), 19),
        (22, "ANA2023001", 100, 40, today + timedelta(days=270), 20.00, today - timedelta(days=7), 20),
        (23, "CIT2023001", 80, 30, today + timedelta(days=240), 30.00, today - timedelta(days=10), 21),
        (24, "VAL2023002", 120, 60, today + timedelta(days=300), 15.00, today - timedelta(days=5), 22),
        (25, "KOR2023001", 60, 20, today + timedelta(days=180), 45.00, today - timedelta(days=15), 23),
        (26, "AMB2023001", 50, 15, today + timedelta(days=210), 60.00, today - timedelta(days=8), 24),
        (27, "LAZ2023001", 70, 25, today + timedelta(days=240), 120.00, today - timedelta(days=12), 25),
        (28, "SME2023001", 90, 40, today + timedelta(days=270), 75.00, today - timedelta(days=7), 1),
        (29, "LIN2023001", 60, 20, today + timedelta(days=210), 160.00, today - timedelta(days=10), 2),
        (30, "ESS2023001", 40, 12, today + timedelta(days=240), 290.00, today - timedelta(days=5), 3),
        (1, "PAR2023003", 80, 30, today + timedelta(days=120), 43.00, today - timedelta(days=3), 4),
        (2, "IBU2023002", 60, 20, today + timedelta(days=90), 72.00, today - timedelta(days=7), 5),
        (3, "AMX2023002", 50, 25, today + timedelta(days=150), 88.00, today - timedelta(days=5), 6),
        (4, "NAZ2023002", 40, 15, today + timedelta(days=60), 115.00, today - timedelta(days=2), 7),
        (5, "NUR2023002", 35, 10, today + timedelta(days=180), 145.00, today - timedelta(days=4), 8),
        (6, "AC2023002", 100, 50, today + timedelta(days=300), 14.00, today - timedelta(days=6), 9),
        (7, "LOP2023002", 80, 30, today + timedelta(days=210), 23.00, today - timedelta(days=8), 10),
        (8, "ASP2023002", 70, 35, today + timedelta(days=270), 42.00, today - timedelta(days=10), 11),
        (9, "SUP2023002", 60, 20, today + timedelta(days=240), 58.00, today - timedelta(days=12), 12),
        (10, "MEZ2023002", 90, 45, today + timedelta(days=330), 42.00, today - timedelta(days=14), 13),
        (11, "GLY2023002", 120, 60, today + timedelta(days=390), 28.00, today - timedelta(days=16), 14),
        (12, "VAL2023003", 150, 80, today + timedelta(days=300), 22.00, today - timedelta(days=18), 15),
        (13, "KAG2023002", 40, 12, today + timedelta(days=210), 115.00, today - timedelta(days=20), 16),
        (14, "ARB2023002", 50, 18, today + timedelta(days=240), 155.00, today - timedelta(days=22), 17),
        (15, "OME2023002", 60, 25, today + timedelta(days=270), 42.00, today - timedelta(days=24), 18),
        (16, "CLA2023002", 70, 30, today + timedelta(days=300), 85.00, today - timedelta(days=26), 19),
        (17, "FEN2023002", 30, 8, today + timedelta(days=210), 205.00, today - timedelta(days=28), 20),
        (18, "MIR2023002", 50, 15, today + timedelta(days=240), 135.00, today - timedelta(days=30), 21),
        (19, "CHL2023002", 100, 45, today + timedelta(days=390), 18.00, today - timedelta(days=32), 22),
        (20, "BEP2023002", 25, 6, today + timedelta(days=210), 255.00, today - timedelta(days=34), 23),
        (21, "PAN2023002", 35, 10, today + timedelta(days=240), 185.00, today - timedelta(days=36), 24),
        (22, "ANA2023002", 80, 35, today + timedelta(days=300), 18.00, today - timedelta(days=38), 25),
        (23, "CIT2023002", 70, 25, today + timedelta(days=270), 28.00, today - timedelta(days=40), 1),
        (24, "VAL2023004", 100, 50, today + timedelta(days=330), 12.00, today - timedelta(days=42), 2),
        (25, "KOR2023002", 50, 15, today + timedelta(days=210), 42.00, today - timedelta(days=44), 3),
        (26, "AMB2023002", 40, 12, today + timedelta(days=240), 55.00, today - timedelta(days=46), 4),
        (27, "LAZ2023002", 60, 20, today + timedelta(days=270), 115.00, today - timedelta(days=48), 5),
        (28, "SME2023002", 80, 35, today + timedelta(days=300), 70.00, today - timedelta(days=50), 6),
        (29, "LIN2023002", 50, 15, today + timedelta(days=240), 155.00, today - timedelta(days=52), 7),
        (30, "ESS2023002", 30, 8, today + timedelta(days=270), 285.00, today - timedelta(days=54), 8)
    ]
    cursor.executemany(
        """INSERT INTO Партии_товаров (
            ТоварID, Номер_партии, Количество_поступления, Количество_остаток, Срок_годности, 
            Цена_закупочная, Дата_поступления, ПоставщикID
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        batches
    )

    # 6. Продажи (100 записей)
    sales = []
    for i in range(100):
        sale_date = today - timedelta(days=random.randint(0, 60))
        employee_id = random.randint(1, 20)
        client_id = random.choice([random.randint(1, 30), None])
        amount = round(random.uniform(100, 2000), 2)
        payment_type = random.choice(['наличные', 'карта', 'онлайн'])
        sales.append((sale_date.strftime('%Y-%m-%d %H:%M:%S'), employee_id, client_id, amount, payment_type)) # Ensure datetime format
    
    cursor.executemany(
        "INSERT INTO Продажи (Дата_время_продажи, СотрудникID, КлиентID, Сумма_продажи, Тип_оплаты) VALUES (?, ?, ?, ?, ?)",
        sales
    )

    # 7. Позиции продаж (200 записей)
    sale_items = []
    for i in range(200):
        sale_id = random.randint(1, 100)
        product_id = random.randint(1, 30)
        
        cursor.execute("SELECT ПартияID FROM Партии_товаров WHERE ТоварID = ?", (product_id,))
        product_batches = cursor.fetchall()
        if not product_batches:
            continue
        batch_id = random.choice(product_batches)[0]
        
        quantity = random.randint(1, 3)
        cursor.execute("SELECT Цена_розничная FROM Товары WHERE ТоварID = ?", (product_id,))
        price = cursor.fetchone()[0]
        
        sale_items.append((sale_id, product_id, batch_id, quantity, price))
    
    cursor.executemany(
        "INSERT INTO Позиции_продаж (ПродажаID, ТоварID, ПартияID, Количество, Цена_продажи) VALUES (?, ?, ?, ?, ?)",
        sale_items
    )

    # 8. Поступления_товаров (25 записей)
    deliveries = []
    for i in range(25):
        supplier_id = random.randint(1, 25) # Assuming 25 suppliers exist
        delivery_date = today - timedelta(days=random.randint(1, 180))
        document_sum = round(random.uniform(5000, 50000), 2)
        deliveries.append((supplier_id, delivery_date.strftime('%Y-%m-%d'), document_sum))

    cursor.executemany(
        "INSERT INTO Поступления_товаров (ПоставщикID, Дата_поступления, Сумма_документа) VALUES (?, ?, ?)",
        deliveries
    )

    # 9. Списания_товаров (15 записей)
    write_offs = []
    for i in range(15):
        write_off_date = today - timedelta(days=random.randint(0, 30))
        employee_id = random.randint(1, 20)
        reason = random.choice(['просрочка', 'брак', 'порча', 'другое'])
        write_offs.append((write_off_date.strftime('%Y-%m-%d'), employee_id, reason))
    
    cursor.executemany(
        "INSERT INTO Списания_товаров (Дата_списания, СотрудникID, Причина) VALUES (?, ?, ?)",
        write_offs
    )

    # 10. Позиции списаний (30 записей)
    write_off_items = []
    for i in range(30):
        write_off_id = random.randint(1, 15) # Assuming 15 write-offs exist
        product_id = random.randint(1, 30)
        
        cursor.execute("SELECT ПартияID FROM Партии_товаров WHERE ТоварID = ?", (product_id,))
        product_batches = cursor.fetchall()
        if not product_batches:
            continue
        batch_id = random.choice(product_batches)[0]
        
        quantity = random.randint(1, 5)
        write_off_items.append((write_off_id, product_id, batch_id, quantity))
    
    cursor.executemany(
        "INSERT INTO Позиции_списаний (СписаниеID, ТоварID, ПартияID, Количество) VALUES (?, ?, ?, ?)",
        write_off_items
    )

    conn.commit()
    conn.close()
    print("Тестовые данные успешно добавлены!")

if __name__ == '__main__':
    add_test_data()