import sqlite3
from datetime import datetime, timedelta
from contextlib import closing

def init_db():
    with closing(sqlite3.connect('pharmacy.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.executescript('''

                CREATE TABLE IF NOT EXISTS Поставщики (
                    ПоставщикID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Наименование TEXT NOT NULL,
                    Контакты TEXT,
                    ИНН TEXT,
                    КПП TEXT
                );

                CREATE TABLE IF NOT EXISTS Сотрудники (
                    СотрудникID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ФИО TEXT NOT NULL,
                    Должность TEXT NOT NULL,
                    Телефон TEXT,
                    Email TEXT
                );

                CREATE TABLE IF NOT EXISTS Клиенты (
                    КлиентID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ФИО TEXT NOT NULL,
                    Телефон TEXT,
                    Номер_карты_лояльности TEXT UNIQUE NULL
                );

                CREATE TABLE IF NOT EXISTS Товары (
                    ТоварID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Наименование TEXT NOT NULL,
                    Категория TEXT,
                    Производитель TEXT,
                    Форма_выпуска TEXT,
                    Дозировка TEXT,
                    Рецептурный INTEGER DEFAULT 0,
                    Цена_розничная REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS Партии_товаров (
                    ПартияID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ТоварID INTEGER NOT NULL,
                    Номер_партии TEXT NOT NULL,
                    Количество_поступления INTEGER NOT NULL,
                    Количество_остаток INTEGER NOT NULL,
                    Срок_годности DATE NOT NULL,
                    Цена_закупочная REAL NOT NULL,
                    Дата_поступления DATE NOT NULL,
                    ПоставщикID INTEGER NOT NULL,
                    FOREIGN KEY (ТоварID) REFERENCES Товары(ТоварID),
                    FOREIGN KEY (ПоставщикID) REFERENCES Поставщики(ПоставщикID)
                );

                CREATE TABLE IF NOT EXISTS Продажи (
                    ПродажаID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Дата_время_продажи DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    СотрудникID INTEGER NOT NULL,
                    КлиентID INTEGER,
                    Сумма_продажи REAL NOT NULL,
                    Тип_оплаты TEXT NOT NULL CHECK(Тип_оплаты IN ('наличные', 'карта', 'онлайн')),
                    FOREIGN KEY (СотрудникID) REFERENCES Сотрудники(СотрудникID),
                    FOREIGN KEY (КлиентID) REFERENCES Клиенты(КлиентID)
                );

                CREATE TABLE IF NOT EXISTS Позиции_продаж (
                    ПозицияID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ПродажаID INTEGER NOT NULL,
                    ТоварID INTEGER NOT NULL,
                    ПартияID INTEGER NOT NULL,
                    Количество INTEGER NOT NULL,
                    Цена_продажи REAL NOT NULL,
                    FOREIGN KEY (ПродажаID) REFERENCES Продажи(ПродажаID),
                    FOREIGN KEY (ТоварID) REFERENCES Товары(ТоварID),
                    FOREIGN KEY (ПартияID) REFERENCES Партии_товаров(ПартияID)
                );

                CREATE TABLE IF NOT EXISTS Поступления_товаров (
                    ПоступлениеID INTEGER PRIMARY KEY AUTOINCREMENT,
                    ПоставщикID INTEGER NOT NULL,
                    Дата_поступления DATE NOT NULL DEFAULT CURRENT_DATE,
                    Сумма_документа REAL NOT NULL,
                    FOREIGN KEY (ПоставщикID) REFERENCES Поставщики(ПоставщикID)
                );

                CREATE TABLE IF NOT EXISTS Списания_товаров (
                    СписаниеID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Дата_списания DATE NOT NULL DEFAULT CURRENT_DATE,
                    СотрудникID INTEGER NOT NULL,
                    Причина TEXT NOT NULL CHECK(Причина IN ('просрочка', 'брак', 'порча', 'другое')),
                    FOREIGN KEY (СотрудникID) REFERENCES Сотрудники(СотрудникID)
                );

                CREATE TABLE IF NOT EXISTS Позиции_списаний (
                    ПозицияID INTEGER PRIMARY KEY AUTOINCREMENT,
                    СписаниеID INTEGER NOT NULL,
                    ТоварID INTEGER NOT NULL,
                    ПартияID INTEGER NOT NULL,
                    Количество INTEGER NOT NULL,
                    FOREIGN KEY (СписаниеID) REFERENCES Списания_товаров(СписаниеID),
                    FOREIGN KEY (ТоварID) REFERENCES Товары(ТоварID),
                    FOREIGN KEY (ПартияID) REFERENCES Партии_товаров(ПартияID)
                );
            ''')
        conn.commit()

def main():
    init_db()

if __name__ == '__main__':
    main()