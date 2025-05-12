import sqlite3
from datetime import date

DB_NAME = 'shop.db'

def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = None
    last_row_id = None

    if commit:
        conn.commit()
        last_row_id = cursor.lastrowid
    if fetchone:
        result = cursor.fetchone()
    if fetchall:
        result = cursor.fetchall()
    
    conn.close()
    return result if not commit else last_row_id

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Товары (
        id_товара INTEGER PRIMARY KEY AUTOINCREMENT,
        название TEXT NOT NULL,
        категория TEXT NOT NULL,
        цена_за_ед REAL NOT NULL CHECK (цена_за_ед > 0),
        кол_на_складе INTEGER NOT NULL CHECK (кол_на_складе >= 0)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Продажи (
        id_чека INTEGER PRIMARY KEY AUTOINCREMENT,
        дата_продажи DATE NOT NULL DEFAULT CURRENT_DATE,
        общая_стоимость REAL NOT NULL CHECK (общая_стоимость >= 0)
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS СоставПродажи (
        id_состава INTEGER PRIMARY KEY AUTOINCREMENT,
        id_чека INTEGER NOT NULL,
        id_товара INTEGER NOT NULL,
        количество INTEGER NOT NULL CHECK (количество > 0),
        цена_на_момент_продажи REAL NOT NULL CHECK (цена_на_момент_продажи > 0),
        FOREIGN KEY (id_чека) REFERENCES Продажи(id_чека) ON DELETE CASCADE,
        FOREIGN KEY (id_товара) REFERENCES Товары(id_товара) ON DELETE RESTRICT
    );
    ''')
    conn.commit()
    conn.close()

def add_product(name, category, price, stock):
    query = "INSERT INTO Товары (название, категория, цена_за_ед, кол_на_складе) VALUES (?, ?, ?, ?)"
    execute_query(query, (name, category, price, stock), commit=True)

def get_all_products():
    query = "SELECT id_товара, название, категория, цена_за_ед, кол_на_складе FROM Товары"
    return execute_query(query, fetchall=True)

def get_product_by_id(product_id):
    query = "SELECT id_товара, название, категория, цена_за_ед, кол_на_складе FROM Товары WHERE id_товара = ?"
    return execute_query(query, (product_id,), fetchone=True)

def update_product_stock(product_id, quantity_sold):
    query = "UPDATE Товары SET кол_на_складе = кол_на_складе - ? WHERE id_товара = ?"
    execute_query(query, (quantity_sold, product_id), commit=True)

def create_sale_record():
    query = "INSERT INTO Продажи (дата_продажи, общая_стоимость) VALUES (date('now'), 0)"
    return execute_query(query, commit=True)

def add_sale_item(check_id, product_id, quantity, price_at_sale):
    query = "INSERT INTO СоставПродажи (id_чека, id_товара, количество, цена_на_момент_продажи) VALUES (?, ?, ?, ?)"
    execute_query(query, (check_id, product_id, quantity, price_at_sale), commit=True)

def update_sale_total_cost(check_id, total_cost):
    query = "UPDATE Продажи SET общая_стоимость = ? WHERE id_чека = ?"
    execute_query(query, (total_cost, check_id), commit=True)

def get_sales_summary_by_date(report_date):
    query = """
    SELECT
        п.id_чека,
        п.дата_продажи,
        п.общая_стоимость,
        GROUP_CONCAT(т.название || ' (' || сп.количество || 'x' || printf('%.2f', сп.цена_на_момент_продажи) || ' руб.)', '; ') AS товары_в_чеке
    FROM Продажи п
    JOIN СоставПродажи сп ON п.id_чека = сп.id_чека
    JOIN Товары т ON сп.id_товара = т.id_товара
    WHERE п.дата_продажи = ?
    GROUP BY п.id_чека, п.дата_продажи, п.общая_стоимость
    ORDER BY п.id_чека;
    """
    return execute_query(query, (report_date,), fetchall=True)

def get_total_revenue_by_date(report_date):
    query = "SELECT SUM(общая_стоимость) AS общая_выручка FROM Продажи WHERE дата_продажи = ?"
    result = execute_query(query, (report_date,), fetchone=True)
    return result[0] if result and result[0] is not None else 0.0

def get_check_details_for_receipt(check_id):
    query = """
    SELECT т.название, сп.количество, сп.цена_на_момент_продажи, (сп.количество * сп.цена_на_момент_продажи) AS сумма_позиции
    FROM СоставПродажи сп
    JOIN Товары т ON сп.id_товара = т.id_товара
    WHERE сп.id_чека = ?;
    """
    return execute_query(query, (check_id,), fetchall=True)

if __name__ == '__main__':
    init_db()
    print("База данных инициализирована.")