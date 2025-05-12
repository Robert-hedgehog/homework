import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QComboBox, QSpinBox, QMessageBox, QDialog, QFormLayout, QHeaderView,
    QTextEdit
)
from PyQt5.QtCore import QDate, Qt, QRegExp
from PyQt5.QtGui import QIntValidator, QRegExpValidator
import database as db

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить новый товар")
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        self.category_edit = QLineEdit()
        self.price_edit = QLineEdit()
        self.stock_edit = QLineEdit()
        
        self.name_cat_regex_pattern = "^[А-Яа-яЁёA-Za-z\\s\\-]+$"
        self.name_cat_validator_regex = QRegExp(self.name_cat_regex_pattern)
        
        name_validator = QRegExpValidator(self.name_cat_validator_regex, self.name_edit)
        self.name_edit.setValidator(name_validator)

        category_validator = QRegExpValidator(self.name_cat_validator_regex, self.category_edit)
        self.category_edit.setValidator(category_validator)

        price_regex = QRegExp("^[0-9]+([,.][0-9]{1,2})?$") 
        price_validator = QRegExpValidator(price_regex, self.price_edit)
        self.price_edit.setValidator(price_validator)

        stock_validator = QIntValidator(0, 999999, self.stock_edit)
        self.stock_edit.setValidator(stock_validator)

        layout.addRow("Название:", self.name_edit)
        layout.addRow("Категория:", self.category_edit)
        layout.addRow("Цена за ед.:", self.price_edit)
        layout.addRow("Кол-во на складе:", self.stock_edit)

        self.buttons_layout = QHBoxLayout()
        self.ok_button = QPushButton("Добавить")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)
        layout.addRow(self.buttons_layout)

    def get_data(self):
        try:
            name = self.name_edit.text().strip()
            category = self.category_edit.text().strip()
            
            price_str = self.price_edit.text().replace(',', '.')
            stock_str = self.stock_edit.text()

            if not name or not category or not price_str or not stock_str:
                 raise ValueError("Все поля должны быть заполнены.")

            final_check_regex = QRegExp(self.name_cat_regex_pattern)
            if not final_check_regex.exactMatch(name):
                raise ValueError("Название содержит недопустимые символы или не соответствует формату (только буквы, пробелы, тире).")
            if not final_check_regex.exactMatch(category):
                raise ValueError("Категория содержит недопустимые символы или не соответствует формату (только буквы, пробелы, тире).")
            
            try:
                price = float(price_str)
            except ValueError:
                raise ValueError("Цена должна быть числом.")
            
            try:
                stock = int(stock_str)
            except ValueError:
                raise ValueError("Количество на складе должно быть целым числом.")
            
            if price <= 0:
                raise ValueError("Цена должна быть положительным числом.")
            if stock < 0:
                raise ValueError("Количество на складе не может быть отрицательным.")
                
            return name, category, price, stock
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", f"Пожалуйста, проверьте введенные данные: {e}")
            return None

class ShopApp(QWidget):
    def __init__(self):
        super().__init__()
        self.cart = []
        self.init_ui()
        self.load_products_to_table()

    def init_ui(self):
        self.setWindowTitle("Система учета товаров в магазине")
        self.setGeometry(100, 100, 1000, 700)
        main_layout = QVBoxLayout(self)

        products_group_layout = QVBoxLayout()
        products_label = QLabel("Товары на складе:")
        products_group_layout.addWidget(products_label)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["ID", "Название", "Категория", "Цена", "На складе"])
        self.products_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.products_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        products_group_layout.addWidget(self.products_table)

        add_product_btn = QPushButton("Добавить товар на склад")
        add_product_btn.clicked.connect(self.show_add_product_dialog)
        products_group_layout.addWidget(add_product_btn)
        
        main_layout.addLayout(products_group_layout)

        cart_formation_layout = QHBoxLayout()
        
        cart_actions_layout = QVBoxLayout()
        cart_actions_label = QLabel("Формирование покупки:")
        cart_actions_layout.addWidget(cart_actions_label)

        self.product_combo = QComboBox()
        cart_actions_layout.addWidget(QLabel("Выберите товар:"))
        cart_actions_layout.addWidget(self.product_combo)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(9999)
        cart_actions_layout.addWidget(QLabel("Количество:"))
        cart_actions_layout.addWidget(self.quantity_spin)

        add_to_cart_btn = QPushButton("Добавить в корзину")
        add_to_cart_btn.clicked.connect(self.add_to_cart)
        cart_actions_layout.addWidget(add_to_cart_btn)
        
        cart_formation_layout.addLayout(cart_actions_layout, 1)

        current_cart_layout = QVBoxLayout()
        cart_label = QLabel("Текущая корзина:")
        current_cart_layout.addWidget(cart_label)
        
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["ID Товара", "Название", "Кол-во", "Цена за ед.", "Сумма"])
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        current_cart_layout.addWidget(self.cart_table)
        
        self.total_cart_cost_label = QLabel("Итоговая стоимость корзины: 0.00 руб.")
        current_cart_layout.addWidget(self.total_cart_cost_label)

        remove_from_cart_btn = QPushButton("Удалить выделенное из корзины")
        remove_from_cart_btn.clicked.connect(self.remove_from_cart)
        current_cart_layout.addWidget(remove_from_cart_btn)
        
        checkout_btn = QPushButton("Оформить покупку")
        checkout_btn.clicked.connect(self.checkout)
        current_cart_layout.addWidget(checkout_btn)

        cart_formation_layout.addLayout(current_cart_layout, 2)
        main_layout.addLayout(cart_formation_layout)

        reports_layout = QVBoxLayout()
        reports_label = QLabel("Отчеты")
        reports_layout.addWidget(reports_label)
        
        show_report_btn = QPushButton("Показать отчет за сегодня")
        show_report_btn.clicked.connect(self.generate_daily_sales_report)
        reports_layout.addWidget(show_report_btn)

        self.report_text_edit = QTextEdit()
        self.report_text_edit.setReadOnly(True)
        reports_layout.addWidget(self.report_text_edit)
        
        main_layout.addLayout(reports_layout)

    def load_products_to_table(self):
        self.products_table.setRowCount(0)
        self.product_combo.clear()
        products = db.get_all_products()
        for row_num, product in enumerate(products):
            self.products_table.insertRow(row_num)
            self.products_table.setItem(row_num, 0, QTableWidgetItem(str(product[0])))
            self.products_table.setItem(row_num, 1, QTableWidgetItem(product[1]))
            self.products_table.setItem(row_num, 2, QTableWidgetItem(product[2]))
            self.products_table.setItem(row_num, 3, QTableWidgetItem(f"{product[3]:.2f}"))
            self.products_table.setItem(row_num, 4, QTableWidgetItem(str(product[4])))
            
            if product[4] > 0:
                 self.product_combo.addItem(f"{product[1]} (ID: {product[0]}, Цена: {product[3]:.2f}, На складе: {product[4]})", product[0])

    def show_add_product_dialog(self):
        dialog = AddProductDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                db.add_product(*data)
                self.load_products_to_table()
                QMessageBox.information(self, "Успех", "Товар успешно добавлен.")

    def add_to_cart(self):
        selected_product_data = self.product_combo.currentData()
        if selected_product_data is None:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите товар.")
            return

        product_id = int(selected_product_data)
        quantity_to_buy = self.quantity_spin.value()

        product_info = db.get_product_by_id(product_id)
        if not product_info:
            QMessageBox.critical(self, "Ошибка", "Товар не найден в базе данных.")
            return

        _, name, _, price_per_unit, stock_available = product_info
        
        current_in_cart_quantity = 0
        for item in self.cart:
            if item[0] == product_id:
                current_in_cart_quantity = item[2]
                break
        
        if quantity_to_buy + current_in_cart_quantity > stock_available:
            QMessageBox.warning(self, "Недостаточно товара", 
                                f"На складе только {stock_available} шт. товара '{name}'.\n"
                                f"В корзине уже: {current_in_cart_quantity} шт.")
            return

        found_in_cart = False
        for i, cart_item in enumerate(self.cart):
            if cart_item[0] == product_id:
                new_quantity = cart_item[2] + quantity_to_buy
                if new_quantity > stock_available:
                     QMessageBox.warning(self, "Недостаточно товара", f"Невозможно добавить {quantity_to_buy} шт. товара '{name}'. Максимум {stock_available - cart_item[2]} шт. с учетом уже в корзине.")
                     return
                self.cart[i] = (product_id, name, new_quantity, price_per_unit, stock_available)
                found_in_cart = True
                break
        
        if not found_in_cart:
            self.cart.append((product_id, name, quantity_to_buy, price_per_unit, stock_available))
        
        self.update_cart_display()

    def update_cart_display(self):
        self.cart_table.setRowCount(0)
        total_cost = 0
        for row_num, item in enumerate(self.cart):
            product_id, name, quantity, price, _ = item
            item_sum = quantity * price
            total_cost += item_sum

            self.cart_table.insertRow(row_num)
            self.cart_table.setItem(row_num, 0, QTableWidgetItem(str(product_id)))
            self.cart_table.setItem(row_num, 1, QTableWidgetItem(name))
            self.cart_table.setItem(row_num, 2, QTableWidgetItem(str(quantity)))
            self.cart_table.setItem(row_num, 3, QTableWidgetItem(f"{price:.2f}"))
            self.cart_table.setItem(row_num, 4, QTableWidgetItem(f"{item_sum:.2f}"))
        
        self.total_cart_cost_label.setText(f"Итоговая стоимость корзины: {total_cost:.2f} руб.")
        self.quantity_spin.setValue(1)

    def remove_from_cart(self):
        selected_rows = self.cart_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Информация", "Выберите товар для удаления из корзины.")
            return
        
        for row_index in sorted([r.row() for r in selected_rows], reverse=True):
            del self.cart[row_index]
        self.update_cart_display()

    def checkout(self):
        if not self.cart:
            QMessageBox.information(self, "Корзина пуста", "Добавьте товары в корзину для оформления покупки.")
            return

        for item_in_cart in self.cart:
            product_id, name, quantity_to_buy, _, _ = item_in_cart
            product_db_info = db.get_product_by_id(product_id)
            if not product_db_info or product_db_info[4] < quantity_to_buy:
                QMessageBox.critical(self, "Ошибка наличия", 
                                     f"Товара '{name}' недостаточно на складе (доступно: {product_db_info[4] if product_db_info else 0}). Пожалуйста, обновите корзину.")
                self.load_products_to_table()
                return

        try:
            check_id = db.create_sale_record()
            if check_id is None:
                raise Exception("Не удалось создать запись о продаже.")

            current_total_cost = 0
            receipt_details = "Чек №: " + str(check_id) + "\nДата: " + QDate.currentDate().toString("yyyy-MM-dd") + "\n\n"
            receipt_details += "Товары:\n"

            for product_id, name, quantity, price_at_sale, _ in self.cart:
                db.add_sale_item(check_id, product_id, quantity, price_at_sale)
                db.update_product_stock(product_id, quantity)
                item_total = quantity * price_at_sale
                current_total_cost += item_total
                receipt_details += f"- {name}: {quantity} шт. x {price_at_sale:.2f} руб. = {item_total:.2f} руб.\n"
            
            db.update_sale_total_cost(check_id, current_total_cost)
            receipt_details += f"\nОбщая стоимость: {current_total_cost:.2f} руб."

            QMessageBox.information(self, "Покупка оформлена", f"Покупка успешно оформлена!\n{receipt_details}")
            
            self.cart = []
            self.update_cart_display()
            self.load_products_to_table()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка оформления", f"Произошла ошибка: {e}")

    def generate_daily_sales_report(self):
        report_date_str = QDate.currentDate().toString("yyyy-MM-dd")
        self.report_text_edit.clear()

        sales_summary = db.get_sales_summary_by_date(report_date_str)
        total_revenue = db.get_total_revenue_by_date(report_date_str)

        report_content = f"--- Отчет по продажам за {report_date_str} ---\n\n"
        
        if sales_summary:
            report_content += "Детализация по чекам:\n"
            for sale in sales_summary:
                check_id, sale_date, total_cost, items_in_check = sale
                report_content += f"  Чек №: {check_id}\n"
                report_content += f"  Дата: {sale_date}\n"
                report_content += f"  Сумма чека: {total_cost:.2f} руб.\n"
                report_content += f"  Купленные товары: {items_in_check}\n"
                report_content += "  -------------------------------------\n"
        else:
            report_content += "За сегодня продаж не было.\n"
        
        report_content += f"\nОбщая выручка за {report_date_str}: {total_revenue:.2f} руб."
        self.report_text_edit.setText(report_content)

if __name__ == '__main__':
    db.init_db()
    app = QApplication(sys.argv)
    shop_window = ShopApp()
    shop_window.show()
    sys.exit(app.exec_())