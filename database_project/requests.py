import sqlite3
from datetime import datetime, timedelta

def connect_db():
    return sqlite3.connect('pharmacy.db')

# 1. Отчет по товарам с истекающим сроком годности
def get_expiring_products(days=30):
    conn = connect_db()
    cursor = conn.cursor()
    end_date = datetime.now() + timedelta(days=days)
    query = """
    SELECT 
        t.Наименование, 
        p.Номер_партии, 
        p.Срок_годности, 
        p.Количество_остаток,
        t.Категория
    FROM Партии_товаров p
    JOIN Товары t ON p.ТоварID = t.ТоварID
    WHERE p.Срок_годности BETWEEN date('now') AND ?
    ORDER BY p.Срок_годности ASC;
    """
    cursor.execute(query, (end_date.strftime('%Y-%m-%d'),))
    results = cursor.fetchall()
    headers = ["Название", "Партия", "Срок годности", "Остаток", "Категория"]
    conn.close()
    return headers, results

# 2. Отчет по товарным остаткам
def get_stock_report():
    conn = connect_db()
    cursor = conn.cursor()
    query = """
    SELECT 
        t.ТоварID, t.Наименование, t.Категория,
        SUM(p.Количество_остаток) as Общий_остаток,
        GROUP_CONCAT(p.Номер_партии || ' (' || p.Количество_остаток || ')', ', ') as Партии
    FROM Товары t
    LEFT JOIN Партии_товаров p ON t.ТоварID = p.ТоварID
    GROUP BY t.ТоварID, t.Наименование, t.Категория
    HAVING Общий_остаток > 0 OR Общий_остаток IS NULL 
    ORDER BY t.Категория, t.Наименование;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    headers = ["ID", "Название", "Категория", "Общий остаток", "Партии (остаток)"]
    conn.close()
    return headers, results

# 3. Анализ продаж за период
def get_sales_report(period_type='month', specific_date=None, year=None, week_or_month_number=None):

    conn = connect_db()
    cursor = conn.cursor()

    if period_type == 'day':
        if not specific_date:
            specific_date = datetime.now().strftime('%Y-%m-%d')
        where_clause = "WHERE date(s.Дата_время_продажи) = date(?)"
        params = [specific_date]
        period_display_format = '%Y-%m-%d'
    elif period_type == 'week':
        if not year or not week_or_month_number:
            now = datetime.now()
            year = year or now.year
            week_or_month_number = week_or_month_number or now.isocalendar()[1]

        where_clause = "WHERE strftime('%Y', s.Дата_время_продажи) = ? AND strftime('%W', s.Дата_время_продажи) = ?"

        params = [str(year), str(week_or_month_number - 1).zfill(2)]
        period_display_format = '%Y-%W'
    elif period_type == 'month':
        if not year or not week_or_month_number:
            now = datetime.now()
            year = year or now.year
            week_or_month_number = week_or_month_number or now.month
        where_clause = "WHERE strftime('%Y-%m', s.Дата_время_продажи) = ?"
        params = [f"{year}-{str(week_or_month_number).zfill(2)}"]
        period_display_format = '%Y-%m'
    else:
        conn.close()
        return ["Ошибка"], [("Неверный тип периода", "", "", "", "")]

    query = f"""
    SELECT 
        strftime('{period_display_format}', s.Дата_время_продажи) as Период,
        t.Категория,
        COUNT(DISTINCT s.ПродажаID) as Количество_продаж,
        SUM(s.Сумма_продажи) as Общая_сумма,
        GROUP_CONCAT(DISTINCT e.ФИО) as Сотрудники
    FROM 
        Продажи s
    JOIN 
        Позиции_продаж ps ON s.ПродажаID = ps.ПродажаID
    JOIN 
        Товары t ON ps.ТоварID = t.ТоварID
    JOIN 
        Сотрудники e ON s.СотрудникID = e.СотрудникID
    {where_clause}
    GROUP BY 
        Период, t.Категория
    ORDER BY 
        Период DESC, Общая_сумма DESC;
    """

    cursor.execute(query, params)
    results = cursor.fetchall()

    headers = ["Период", "Категория", "Кол-во продаж", "Сумма", "Сотрудники"]
    conn.close()
    return headers, results

# 4. Дефектура (товары с низким остатком)
def get_low_stock_products(min_level=5):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
    SELECT 
        t.ТоварID, t.Наименование, t.Категория,
        COALESCE(SUM(p.Количество_остаток), 0) as Общий_остаток
    FROM Товары t
    LEFT JOIN Партии_товаров p ON t.ТоварID = p.ТоварID
    GROUP BY t.ТоварID, t.Наименование, t.Категория
    HAVING Общий_остаток < ? OR Общий_остаток IS NULL
    ORDER BY Общий_остаток ASC;
    """
    cursor.execute(query, (min_level,))
    results = cursor.fetchall()
    headers = ["ID", "Название", "Категория", "Остаток"]
    conn.close()
    return headers, results

# 5. Формирование заявки поставщику
def generate_supplier_order(sales_days=30, min_stock=10):
    conn = connect_db()
    cursor = conn.cursor()
    query = """
    WITH ProductSales AS (
        SELECT 
            ps.ТоварID, 
            SUM(ps.Количество) as Количество
        FROM Позиции_продаж ps
        JOIN Продажи s ON ps.ПродажаID = s.ПродажаID
        WHERE s.Дата_время_продажи >= date('now', ?)
        GROUP BY ps.ТоварID
    ),
    ProductStock AS (
        SELECT
            ТоварID,
            SUM(Количество_остаток) as Текущий_остаток
        FROM Партии_товаров
        GROUP BY ТоварID
    ),
    LastSupplier AS ( -- Определение последнего поставщика для каждого товара
        SELECT
            pt.ТоварID,
            s.Наименование as ПоставщикНаименование,
            ROW_NUMBER() OVER (PARTITION BY pt.ТоварID ORDER BY pt.Дата_поступления DESC, pt.ПартияID DESC) as rn
        FROM Партии_товаров pt
        JOIN Поставщики s ON pt.ПоставщикID = s.ПоставщикID
    )
    SELECT 
        t.ТоварID,
        t.Наименование,
        t.Производитель,
        COALESCE(psk.Текущий_остаток, 0) as Текущий_остаток,
        COALESCE(psa.Количество, 0) as Продано_за_период,
        CASE 
            WHEN COALESCE(psk.Текущий_остаток, 0) < ? THEN 'СРОЧНЫЙ ЗАКАЗ'
            ELSE 'ПЛАНОВЫЙ ЗАКАЗ'
        END as Приоритет,
        ls.ПоставщикНаименование as Основной_поставщик
    FROM Товары t
    LEFT JOIN ProductStock psk ON t.ТоварID = psk.ТоварID
    LEFT JOIN ProductSales psa ON t.ТоварID = psa.ТоварID
    LEFT JOIN LastSupplier ls ON t.ТоварID = ls.ТоварID AND ls.rn = 1 -- Только самый последний поставщик
    WHERE 
        COALESCE(psk.Текущий_остаток, 0) < ? OR COALESCE(psa.Количество, 0) > 0 -- Убрал *2 для min_stock в HAVING
    ORDER BY 
        Приоритет DESC, Продано_за_период DESC;
    """
    cursor.execute(query, (f"-{sales_days} days", min_stock, min_stock))
    results = cursor.fetchall()
    headers = ["ID", "Название", "Производитель", "Остаток", "Продано", "Приоритет", "Поставщик"]
    conn.close()
    return headers, results

# 6. Отчет по движению товара
def get_product_movement(product_id, start_date, end_date):
    conn = connect_db()
    cursor = conn.cursor()
    query_receipt = """
    SELECT 'Поступление' as Тип, pp.Наименование as Источник, pt.Номер_партии,
           pt.Количество_поступления as Количество, pt.Дата_поступления as Дата, pt.Цена_закупочная as Цена
    FROM Партии_товаров pt
    JOIN Поставщики pp ON pt.ПоставщикID = pp.ПоставщикID
    WHERE pt.ТоварID = ? AND pt.Дата_поступления BETWEEN ? AND ?
    """
    query_sales = """
    SELECT 'Продажа' as Тип, e.ФИО as Источник, pt.Номер_партии,
           SUM(ps.Количество) as Количество, strftime('%Y-%m-%d', s.Дата_время_продажи) as Дата, AVG(ps.Цена_продажи) as Цена
    FROM Позиции_продаж ps
    JOIN Продажи s ON ps.ПродажаID = s.ПродажаID
    JOIN Сотрудники e ON s.СотрудникID = e.СотрудникID
    JOIN Партии_товаров pt ON ps.ПартияID = pt.ПартияID
    WHERE ps.ТоварID = ? AND date(s.Дата_время_продажи) BETWEEN ? AND ?
    GROUP BY strftime('%Y-%m-%d', s.Дата_время_продажи), e.ФИО, pt.Номер_партии
    """
    query_write_off = """
    SELECT 'Списание' as Тип, wo.Причина as Источник, pt.Номер_партии,
           SUM(woi.Количество) as Количество, wo.Дата_списания as Дата, NULL as Цена
    FROM Позиции_списаний woi
    JOIN Списания_товаров wo ON woi.СписаниеID = wo.СписаниеID
    JOIN Партии_товаров pt ON woi.ПартияID = pt.ПартияID
    WHERE woi.ТоварID = ? AND wo.Дата_списания BETWEEN ? AND ?
    GROUP BY wo.Дата_списания, wo.Причина, pt.Номер_партии
    """
    product_info = conn.execute("SELECT Наименование FROM Товары WHERE ТоварID = ?", (product_id,)).fetchone()
    if not product_info:
        conn.close()
        return ["Ошибка"], [("Товар с таким ID не найден.", "", "", "", "", "")] # Возвращаем в формате headers, data

    product_name = product_info[0]

    cursor.execute(f"{query_receipt} UNION ALL {query_sales} UNION ALL {query_write_off} ORDER BY Дата", 
                  (product_id, start_date, end_date, product_id, start_date, end_date, product_id, start_date, end_date))
    results = cursor.fetchall()
    headers = ["Тип", f"Источник/Инфо ({product_name})", "Партия", "Количество", "Дата", "Цена"]
    conn.close()
    return headers, results

if __name__ == "__main__":
    from tabulate import tabulate

    print("\n=== Тестирование запросов (возврат данных) ===\n")

    hdrs, res = get_expiring_products(days=90)
    print(f"\n1. Товары с истекающим сроком годности (90 дней):\n{tabulate(res, headers=hdrs, tablefmt='grid')}")

    hdrs, res = get_stock_report()
    print(f"\n2. Отчёт по остаткам:\n{tabulate(res, headers=hdrs, tablefmt='grid')}")
    
    hdrs, res = get_sales_report(period='month')
    print(f"\n3. Анализ продаж за месяц:\n{tabulate(res, headers=hdrs, tablefmt='grid')}")

    hdrs, res = get_low_stock_products(min_level=10)
    print(f"\n4. Товары с остатком < 10:\n{tabulate(res, headers=hdrs, tablefmt='grid')}")

    hdrs, res = generate_supplier_order(sales_days=30, min_stock=20)
    print(f"\n5. Рекомендации по заказу:\n{tabulate(res, headers=hdrs, tablefmt='grid')}")

    today = datetime.now().strftime('%Y-%m-%d')
    month_ago = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')

    try:
        product_id_to_test = 1

        conn_test = connect_db()
        exists = conn_test.execute("SELECT 1 FROM Товары WHERE ТоварID = ?", (product_id_to_test,)).fetchone()
        conn_test.close()

        if exists:
             hdrs, res = get_product_movement(product_id=product_id_to_test, start_date=month_ago, end_date=today)
             print(f"\n6. Движение товара (ID={product_id_to_test}, {month_ago} - {today}):\n{tabulate(res, headers=hdrs, tablefmt='grid')}")
        else:
            print(f"\n6. Движение товара: Товар с ID={product_id_to_test} не найден для теста.")

    except sqlite3.Error as e:
        print(f"Ошибка SQLite при тестировании get_product_movement: {e}")
    except Exception as e:
        print(f"Другая ошибка при тестировании: {e}")


    print("\n=== Тестирование завершено ===")