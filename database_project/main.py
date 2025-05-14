import sys
import sqlite3
import traceback
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTableWidgetItem, QMessageBox,
                             QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QListWidgetItem,
                             QLabel, QSpinBox, QDateEdit, QComboBox, QCheckBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt, QDate
from tabulate import tabulate

import BD
import requests
import data

class BaseAddDialog(QDialog):
    def __init__(self, title, fields_config, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.fields_config = fields_config
        self.field_widgets = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        for field_name, config in self.fields_config.items():
            label_text = config["label"]
            widget_type = config["widget_type"]
            widget_args = config.get("args", {})
            widget = widget_type(**widget_args)
            if isinstance(widget, QDoubleSpinBox):
                widget.setDecimals(2)
                widget.setMinimum(config.get("min_val", 0.00))
                widget.setMaximum(config.get("max_val", 9999999.99))
                if "default" in config: widget.setValue(config["default"])
            elif isinstance(widget, QSpinBox):
                widget.setMinimum(config.get("min_val", 0))
                widget.setMaximum(config.get("max_val", 999999))
                if "default" in config: widget.setValue(config["default"])
            elif isinstance(widget, QDateEdit):
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("yyyy-MM-dd")
                if "default_offset_days" in config:
                    widget.setDate(QDate.currentDate().addDays(config["default_offset_days"]))
                elif "default" in config:
                     widget.setDate(QDate.fromString(config["default"], "yyyy-MM-dd"))
                else:
                    widget.setDate(QDate.currentDate())
            elif isinstance(widget, QLineEdit) and "placeholder" in config:
                widget.setPlaceholderText(config["placeholder"])
            layout.addRow(label_text, widget)
            self.field_widgets[field_name] = widget
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        form_data = {}
        for field_name, widget in self.field_widgets.items():
            config = self.fields_config[field_name]
            is_required = config.get("required", False)
            value = None
            if isinstance(widget, QLineEdit):
                value = widget.text()
            elif isinstance(widget, QDoubleSpinBox):
                value = widget.value()
            elif isinstance(widget, QSpinBox):
                value = widget.value()
            elif isinstance(widget, QDateEdit):
                value = widget.date().toString(Qt.ISODate)
            elif isinstance(widget, QCheckBox):
                value = 1 if widget.isChecked() else 0
            
            if is_required and (value == "" or (isinstance(value, (float, int)) and value == 0 and config.get("allow_zero", False) is False)):
                QMessageBox.warning(self, "Ошибка ввода", f"Поле '{config['label']}' обязательно."); return None
            form_data[field_name] = value if value != "" else None
        return form_data

class AddSotrudnikDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {"fio": {"label": "ФИО*:", "widget_type": QLineEdit, "required": True}, "dolzhnost": {"label": "Должность*:", "widget_type": QLineEdit, "required": True}, "phone": {"label": "Телефон:", "widget_type": QLineEdit}, "email": {"label": "Email:", "widget_type": QLineEdit}}
        super().__init__("Добавить сотрудника", fields, parent)

class AddKlientDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {"fio": {"label": "ФИО*:", "widget_type": QLineEdit, "required": True}, "phone": {"label": "Телефон:", "widget_type": QLineEdit}, "loyalty_card": {"label": "Карта лояльности:", "widget_type": QLineEdit}}
        super().__init__("Добавить клиента", fields, parent)

class AddPostavshikDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {"name": {"label": "Наименование*:", "widget_type": QLineEdit, "required": True}, "contacts": {"label": "Контакты:", "widget_type": QLineEdit}, "inn": {"label": "ИНН:", "widget_type": QLineEdit}, "kpp": {"label": "КПП:", "widget_type": QLineEdit}}
        super().__init__("Добавить поставщика", fields, parent)

class AddTovarDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {"name": {"label": "Наименование*:", "widget_type": QLineEdit, "required": True}, "category": {"label": "Категория:", "widget_type": QLineEdit}, "manufacturer": {"label": "Производитель:", "widget_type": QLineEdit}, "form": {"label": "Форма выпуска:", "widget_type": QLineEdit}, "dosage": {"label": "Дозировка:", "widget_type": QLineEdit}, "prescription": {"label": "Рецептурный:", "widget_type": QCheckBox}, "price": {"label": "Цена розничная*:", "widget_type": QDoubleSpinBox, "required": True, "min_val": 0.01, "allow_zero": False}}
        super().__init__("Добавить товар", fields, parent)

class AddPartiyaDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {
            "tovar_id": {"label": "ID Товара*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "nomer_partii": {"label": "Номер партии*:", "widget_type": QLineEdit, "required": True},
            "kolichestvo_postupleniya": {"label": "Количество поступления*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "srok_godnosti": {"label": "Срок годности*:", "widget_type": QDateEdit, "required": True},
            "cena_zakupki": {"label": "Цена закупки*:", "widget_type": QDoubleSpinBox, "required": True, "min_val": 0.01},
            "data_postavki": {"label": "Дата поставки*:", "widget_type": QDateEdit, "required": True, "default_offset_days": 0},
            "postavshik_id": {"label": "ID Поставщика*:", "widget_type": QSpinBox, "required": True, "min_val": 1}
        }
        super().__init__("Добавить партию товара", fields, parent)

class AddPozitsiyaProdazhiDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {
            "prodazha_id": {"label": "ID Продажи*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "tovar_id": {"label": "ID Товара*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "partiya_id": {"label": "ID Партии*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "kolichestvo": {"label": "Количество*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "tsena_prodazhi_za_edinitcu": {"label": "Цена продажи за ед.*:", "widget_type": QDoubleSpinBox, "required": True, "min_val": 0.01}
        }
        super().__init__("Добавить позицию продажи", fields, parent)

class AddPostuplenieDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {
            "postavshik_id": {"label": "ID Поставщика*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "data_postupleniya": {"label": "Дата поступления*:", "widget_type": QDateEdit, "required": True, "default_offset_days": 0},
            "summa_dokumenta": {"label": "Сумма документа*:", "widget_type": QDoubleSpinBox, "required": True, "min_val": 0.01}
        }
        super().__init__("Добавить поступление товаров", fields, parent)

class AddPozitsiyaSpisaniyaDialog(BaseAddDialog):
    def __init__(self, parent=None):
        fields = {
            "spisanie_id": {"label": "ID Списания*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "tovar_id": {"label": "ID Товара*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "partiya_id": {"label": "ID Партии*:", "widget_type": QSpinBox, "required": True, "min_val": 1},
            "kolichestvo": {"label": "Количество*:", "widget_type": QSpinBox, "required": True, "min_val": 1}
        }
        super().__init__("Добавить позицию списания", fields, parent)


class AddProdazhaDialog(QDialog):
    def __init__(self, kassiri_list, parent=None):
        super().__init__(parent); self.setWindowTitle("Оформить продажу"); layout = QFormLayout(self)
        self.sotrudnik_combo = QComboBox(self)
        for sotrudnik_id, fio in kassiri_list: self.sotrudnik_combo.addItem(fio, sotrudnik_id)
        layout.addRow("Кассир*:", self.sotrudnik_combo)
        self.summa_edit = QDoubleSpinBox(self); self.summa_edit.setMinimum(0.01); layout.addRow("Сумма*:", self.summa_edit)
        self.tip_oplaty_combo = QComboBox(self); self.tip_oplaty_combo.addItems(['наличные', 'карта', 'онлайн'])
        layout.addRow("Тип оплаты*:", self.tip_oplaty_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
    def get_data(self):
        if self.sotrudnik_combo.currentIndex() == -1: QMessageBox.warning(self, "Ошибка", "Не выбран кассир."); return None
        if self.summa_edit.value() < 0.01: QMessageBox.warning(self, "Ошибка", "Сумма продажи > 0."); return None
        return {"sotrudnik_id": self.sotrudnik_combo.currentData(), "summa_prodazhi": self.summa_edit.value(), "tip_oplaty": self.tip_oplaty_combo.currentText()}

class AddSpisanieDialog(QDialog):
    def __init__(self, farmacevty_provizory_list, parent=None):
        super().__init__(parent); self.setWindowTitle("Оформить списание"); layout = QFormLayout(self)
        self.sotrudnik_combo = QComboBox(self)
        for sotrudnik_id, fio in farmacevty_provizory_list: self.sotrudnik_combo.addItem(fio, sotrudnik_id)
        layout.addRow("Сотрудник (Фармацевт/Провизор)*:", self.sotrudnik_combo)
        self.prichina_combo = QComboBox(self); self.prichina_combo.addItems(['просрочка', 'брак', 'порча', 'другое'])
        layout.addRow("Причина*:", self.prichina_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
    def get_data(self):
        if self.sotrudnik_combo.currentIndex() == -1: QMessageBox.warning(self, "Ошибка", "Не выбран сотрудник."); return None
        return {"sotrudnik_id": self.sotrudnik_combo.currentData(), "prichina": self.prichina_combo.currentText()}

Ui_MainWindow, QtBaseClass = uic.loadUiType("mainwindow.ui")

class PharmacyApp(QMainWindow, Ui_MainWindow):
    DB_NAME = 'pharmacy.db'
    def __init__(self):
        super().__init__(); self.setupUi(self)
        self._configure_menu_and_reports(); self._init_ui_elements(); self._connect_signals(); self._set_initial_page()

    def _configure_menu_and_reports(self):
        self.menu_config = {
            "Сотрудники": {"page": self.page_Sotrudniki, "widget": self.tableWidget_Sotrudniki, "cols": ["ID", "ФИО", "Должность", "Телефон", "Email"], "db": "Сотрудники", "id_col": "СотрудникID", "add_dialog": AddSotrudnikDialog, "add_btn": self.pushButton_AddSotrudnik, "del_btn": self.pushButton_DeleteSotrudnik},
            "Клиенты": {"page": self.page_Klienti, "widget": self.tableWidget_Klienti, "cols": ["ID", "ФИО", "Телефон", "Карта лояльности"], "db": "Клиенты", "id_col": "КлиентID", "add_dialog": AddKlientDialog, "add_btn": self.pushButton_AddKlient, "del_btn": self.pushButton_DeleteKlient},
            "Поставщики": {"page": self.page_Postavshiki, "widget": self.tableWidget_Postavshiki, "cols": ["ID", "Наименование", "Контакты", "ИНН", "КПП"], "db": "Поставщики", "id_col": "ПоставщикID", "add_dialog": AddPostavshikDialog, "add_btn": self.pushButton_AddPostavshik, "del_btn": self.pushButton_DeletePostavshik},
            "Товары": {"page": self.page_Tovari, "widget": self.tableWidget_Tovari, "cols": ["ID", "Наименование", "Категория", "Производитель", "Форма", "Дозировка", "Рецепт", "Цена"], "db": "Товары", "id_col": "ТоварID", "add_dialog": AddTovarDialog, "add_btn": self.pushButton_AddTovar, "del_btn": self.pushButton_DeleteTovar},
            "Партии товаров": {"page": self.page_PartiiTovarov, "widget": self.tableWidget_PartiiTovarov, "cols": ["ID", "ТоварID", "№ Партии", "Поступление", "Остаток", "Срок годности", "Цена заказа", "Дата поставки", "ПостID"], "db": "Партии_товаров", "id_col": "ПартияID", "add_dialog": AddPartiyaDialog, "add_btn": self.pushButton_AddPartiya, "del_btn": self.pushButton_DeletePartiya},
            "Продажи": {"page": self.page_Prodazhi, "widget": self.tableWidget_Prodazhi, "cols": ["ID", "Дата", "СотрудникID", "КлиентID", "Сумма", "Тип оплаты"], "db": "Продажи", "id_col": "ПродажаID", "add_handler_name": "handle_add_prodazha", "add_btn": self.pushButton_AddProdazha, "del_btn": self.pushButton_DeleteProdazha},
            "Позиции продаж": {"page": self.page_PozitsiiProdazh, "widget": self.tableWidget_PozitsiiProdazh, "cols": ["ID", "ПродажаID", "ТоварID", "ПартияID", "Кол-во", "Цена"], "db": "Позиции_продаж", "id_col": "ПозицияID", "add_dialog": AddPozitsiyaProdazhiDialog, "add_btn": self.pushButton_AddPozitsiyaProdazhi, "del_btn": self.pushButton_DeletePozitsiyaProdazhi},
            "Поступления товаров": {"page": self.page_PostupleniyaTovarov, "widget": self.tableWidget_PostupleniyaTovarov, "cols": ["ID", "ПоставщикID", "Дата", "Сумма"], "db": "Поступления_товаров", "id_col": "ПоступлениеID", "add_dialog": AddPostuplenieDialog, "add_btn": self.pushButton_AddPostuplenie, "del_btn": self.pushButton_DeletePostuplenie},
            "Списания товаров": {"page": self.page_SpisaniyaTovarov, "widget": self.tableWidget_SpisaniyaTovarov, "cols": ["ID", "Дата", "СотрудникID", "Причина"], "db": "Списания_товаров", "id_col": "СписаниеID", "add_handler_name": "handle_add_spisanie", "add_btn": self.pushButton_AddSpisanie, "del_btn": self.pushButton_DeleteSpisanie},
            "Позиции списаний": {"page": self.page_PozitsiiSpisaniy, "widget": self.tableWidget_PozitsiiSpisaniy, "cols": ["ID", "СписаниеID", "ТоварID", "ПартияID", "Кол-во"], "db": "Позиции_списаний", "id_col": "ПозицияID", "add_dialog": AddPozitsiyaSpisaniyaDialog, "add_btn": self.pushButton_AddPozitsiyaSpisaniya, "del_btn": self.pushButton_DeletePozitsiyaSpisaniya},
        }

        self.reports_definitions = {
            "Товары с истекающим сроком годности": {"function": requests.get_expiring_products, "params": [{"name": "days", "label": "Дней до истечения:", "widget_type": QSpinBox, "default": 30, "min": 1, "max": 365}]},
            "Отчет по товарным остаткам": {"function": requests.get_stock_report, "params": []},
            "Анализ продаж за период": {"function": requests.get_sales_report, "params": [{"name": "period_type", "label": "Тип периода:", "widget_type": QComboBox, "options": ["day", "week", "month"], "default": "month", "triggers_update": True}, {"name": "specific_date", "label": "Дата (ГГГГ-ММ-ДД):", "widget_type": QDateEdit, "visible_on": ["day"], "default_offset_days": 0}, {"name": "year", "label": "Год:", "widget_type": QSpinBox, "min": 2000, "max": 2099, "visible_on": ["week", "month"]}, {"name": "week_number", "label": "Номер недели (1-53):", "widget_type": QSpinBox, "min": 1, "max": 53, "visible_on": ["week"]}, {"name": "month_number", "label": "Номер месяца (1-12):", "widget_type": QSpinBox, "min": 1, "max": 12, "visible_on": ["month"]}]},
            "Дефектура (товары с низким остатком)": {"function": requests.get_low_stock_products, "params": [{"name": "min_level", "label": "Минимальный уровень:", "widget_type": QSpinBox, "default": 5, "min": 0, "max": 1000}]},
            "Формирование заявки поставщику": {"function": requests.generate_supplier_order, "params": [{"name": "sales_days", "label": "Анализ продаж за (дней):", "widget_type": QSpinBox, "default": 30, "min": 1, "max": 365}, {"name": "min_stock", "label": "Мин. остаток для заказа:", "widget_type": QSpinBox, "default": 10, "min": 0, "max": 1000}]},
            "Отчет по движению товара": {"function": requests.get_product_movement, "params": [{"name": "product_id", "label": "ID Товара:", "widget_type": QLineEdit, "placeholder": "Введите ID товара"}, {"name": "start_date", "label": "Начальная дата:", "widget_type": QDateEdit, "default_offset_days": -30}, {"name": "end_date", "label": "Конечная дата:", "widget_type": QDateEdit, "default_offset_days": 0}]}
        }
        self.current_report_param_widgets = {}

    def _init_ui_elements(self):
        for item_name in self.menu_config.keys(): self.listWidget_Menu.addItem(QListWidgetItem(item_name))
        for config in self.menu_config.values():
            table = config["widget"]
            table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers); table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection); table.verticalHeader().setVisible(False)
        self.comboBox_ReportType.addItems(self.reports_definitions.keys())
        self.formLayout_ReportParams.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        self.textEdit_ReportOutput.setFontFamily("Monospace")

    def _connect_signals(self):
        self.listWidget_Menu.currentItemChanged.connect(self.on_menu_item_changed)
        self.pushButton_ToggleReports.clicked.connect(self.toggle_reports_page)
        for item_name, config in self.menu_config.items():
            if "add_btn" in config and config["add_btn"]:
                if hasattr(config["add_btn"], 'clicked'):
                    if "add_handler_name" in config and hasattr(self, config["add_handler_name"]): config["add_btn"].clicked.connect(getattr(self, config["add_handler_name"]))
                    elif "add_dialog" in config: config["add_btn"].clicked.connect(lambda checked=False, name=item_name: self.handle_add_item(name))
            if "del_btn" in config and config["del_btn"]:
                 if hasattr(config["del_btn"], 'clicked'):
                    config["del_btn"].clicked.connect(lambda checked=False, name=item_name: self.handle_delete_item(name))
        self.comboBox_ReportType.currentIndexChanged.connect(self.update_report_params_ui)
        self.pushButton_GenerateReport.clicked.connect(self.run_selected_report)

    def _set_initial_page(self):
        self.stackedWidget_Content.setCurrentWidget(self.page_Placeholder)
        if self.listWidget_Menu.count() > 0: self.listWidget_Menu.setCurrentRow(0)

    def on_menu_item_changed(self, current, previous):
        if current:
            item_name = current.text()
            if item_name in self.menu_config:
                config = self.menu_config[item_name]; self.stackedWidget_Content.setCurrentWidget(config["page"]); self.load_data_into_table(item_name)

    def toggle_reports_page(self):
        if self.stackedWidget_Content.currentWidget() == self.page_Reports:
            if self.listWidget_Menu.count() > 0 : self.listWidget_Menu.setCurrentRow(0)
            else: self.stackedWidget_Content.setCurrentWidget(self.page_Placeholder)
        else:
            self.listWidget_Menu.clearSelection(); self.stackedWidget_Content.setCurrentWidget(self.page_Reports); self.update_report_params_ui()

    def load_data_into_table(self, item_name_key):
        if item_name_key not in self.menu_config: return
        config = self.menu_config[item_name_key]; table_widget = config["widget"]; columns = config["cols"]; db_table = config["db"]
        table_widget.clearContents(); table_widget.setRowCount(0); table_widget.setColumnCount(len(columns)); table_widget.setHorizontalHeaderLabels(columns)
        data_rows = self._execute_query(f"SELECT * FROM {db_table}", fetch_all=True)
        if data_rows:
            table_widget.setRowCount(len(data_rows))
            for row_idx, row_data in enumerate(data_rows):
                for col_idx, cell_data in enumerate(row_data):

                    if item_name_key == "Продажи" and col_idx == 1 and cell_data is not None:
                        cell_display_data = str(cell_data).split(' ')[0]

                    elif item_name_key == "Списания товаров" and col_idx == 1 and cell_data is not None:
                         cell_display_data = str(cell_data).split(' ')[0]
                    else:
                        cell_display_data = str(cell_data) if cell_data is not None else ""
                    table_widget.setItem(row_idx, col_idx, QTableWidgetItem(cell_display_data))
        table_widget.resizeColumnsToContents()

    def get_sotrudniki_by_dolzhnost(self, dolzhnosti):
        if not isinstance(dolzhnosti, list): dolzhnosti = [dolzhnosti]
        placeholders = ', '.join(['?'] * len(dolzhnosti))
        query = f"SELECT СотрудникID, ФИО FROM Сотрудники WHERE Должность IN ({placeholders})"
        return self._execute_query(query, dolzhnosti, fetch_all=True) or []

    def handle_add_item(self, item_name_key):
        if item_name_key not in self.menu_config: return
        config = self.menu_config[item_name_key]; dialog_class = config.get("add_dialog")
        if not dialog_class: QMessageBox.information(self, "Информация", f"Добавление для '{item_name_key}' не реализовано."); return
        dialog = dialog_class(self)
        if dialog.exec_():
            form_data = dialog.get_data()
            if form_data:
                db_table = config["db"]
                query = None; params = None
                if db_table == "Клиенты" and form_data.get("loyalty_card") and self._execute_query("SELECT 1 FROM Клиенты WHERE Номер_карты_лояльности = ?", (form_data["loyalty_card"],), fetch_one=True):
                    QMessageBox.warning(self, "Ошибка", "Карта лояльности уже существует."); return
                
                if db_table == "Сотрудники": query = "INSERT INTO Сотрудники (ФИО, Должность, Телефон, Email) VALUES (?, ?, ?, ?)"; params = (form_data["fio"], form_data["dolzhnost"], form_data["phone"], form_data["email"])
                elif db_table == "Клиенты": query = "INSERT INTO Клиенты (ФИО, Телефон, Номер_карты_лояльности) VALUES (?, ?, ?)"; params = (form_data["fio"], form_data["phone"], form_data["loyalty_card"])
                elif db_table == "Поставщики": query = "INSERT INTO Поставщики (Наименование, Контакты, ИНН, КПП) VALUES (?, ?, ?, ?)"; params = (form_data["name"], form_data["contacts"], form_data["inn"], form_data["kpp"])
                elif db_table == "Товары": query = "INSERT INTO Товары (Наименование, Категория, Производитель, Форма_выпуска, Дозировка, Рецептурный, Цена_розничная) VALUES (?, ?, ?, ?, ?, ?, ?)"; params = (form_data["name"], form_data["category"], form_data["manufacturer"], form_data["form"], form_data["dosage"], form_data["prescription"], form_data["price"])
                elif db_table == "Партии_товаров": query = "INSERT INTO Партии_товаров (ТоварID, Номер_партии, Количество_поступления, Количество_остаток, Срок_годности, Цена_закупки, Дата_поставки, ПоставщикID) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"; params = (form_data["tovar_id"], form_data["nomer_partii"], form_data["kolichestvo_postupleniya"], form_data["kolichestvo_postupleniya"], form_data["srok_godnosti"], form_data["cena_zakupki"], form_data["data_postavki"], form_data["postavshik_id"])
                elif db_table == "Позиции_продаж": query = "INSERT INTO Позиции_продаж (ПродажаID, ТоварID, ПартияID, Количество, Цена_продажи_за_единицу) VALUES (?, ?, ?, ?, ?)"; params = (form_data["prodazha_id"], form_data["tovar_id"], form_data["partiya_id"], form_data["kolichestvo"], form_data["tsena_prodazhi_za_edinitcu"])
                elif db_table == "Поступления_товаров": query = "INSERT INTO Поступления_товаров (ПоставщикID, Дата_поступления, Сумма_документа) VALUES (?, ?, ?)"; params = (form_data["postavshik_id"], form_data["data_postupleniya"], form_data["summa_dokumenta"])
                elif db_table == "Позиции_списаний": query = "INSERT INTO Позиции_списаний (СписаниеID, ТоварID, ПартияID, Количество) VALUES (?, ?, ?, ?)"; params = (form_data["spisanie_id"], form_data["tovar_id"], form_data["partiya_id"], form_data["kolichestvo"])
                else: QMessageBox.warning(self, "Ошибка", f"Логика добавления для {db_table} не определена."); return
                
                if query and self._execute_query(query, params, commit=True):
                    QMessageBox.information(self, "Успех", f"Запись в '{item_name_key}' добавлена."); self.load_data_into_table(item_name_key)

    def handle_delete_item(self, item_name_key):
        if item_name_key not in self.menu_config: return
        config = self.menu_config[item_name_key]; table_widget = config["widget"]; db_table = config["db"]; id_column_name = config["id_col"]
        selected_rows = table_widget.selectionModel().selectedRows()
        if not selected_rows: QMessageBox.warning(self, "Удаление", "Выберите строку."); return
        id_item = table_widget.item(selected_rows[0].row(), 0)
        if not id_item: QMessageBox.warning(self, "Ошибка", "Не удалось получить ID."); return
        item_id = id_item.text()
        if QMessageBox.question(self, "Подтверждение", f"Удалить ID {item_id} из '{db_table}'?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            if self._execute_query(f"DELETE FROM {db_table} WHERE {id_column_name} = ?", (item_id,), commit=True):
                QMessageBox.information(self, "Успех", "Запись удалена."); self.load_data_into_table(item_name_key)

    def handle_add_prodazha(self):
        kassiri = self.get_sotrudniki_by_dolzhnost(["Кассир"])
        if not kassiri: QMessageBox.warning(self, "Ошибка", "Нет кассиров."); return
        dialog = AddProdazhaDialog(kassiri, self)
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                s_info = self._execute_query("SELECT Должность FROM Сотрудники WHERE СотрудникID = ?", (data["sotrudnik_id"],), fetch_one=True)
                if not s_info or s_info[0] != "Кассир": QMessageBox.critical(self, "Ошибка", "Сотрудник не кассир!"); return
                p_id = self._execute_query("INSERT INTO Продажи (СотрудникID, Сумма_продажи, Тип_оплаты) VALUES (?, ?, ?)", (data["sotrudnik_id"], data["summa_prodazhi"], data["tip_oplaty"]), commit=True, get_last_rowid=True)
                if p_id: QMessageBox.information(self, "Успех", f"Продажа (ID: {p_id}) оформлена (упрощенно)."); self.load_data_into_table("Продажи")

    def handle_add_spisanie(self):
        farm_prov = self.get_sotrudniki_by_dolzhnost(["Фармацевт", "Провизор"])
        if not farm_prov: QMessageBox.warning(self, "Ошибка", "Нет фармацевтов/провизоров."); return
        dialog = AddSpisanieDialog(farm_prov, self)
        if dialog.exec_():
            data = dialog.get_data()
            if data:
                s_info = self._execute_query("SELECT Должность FROM Сотрудники WHERE СотрудникID = ?", (data["sotrudnik_id"],), fetch_one=True)
                if not s_info or s_info[0] not in ["Фармацевт", "Провизор"]: QMessageBox.critical(self, "Ошибка", "Сотрудник не фармацевт/провизор!"); return
                s_id = self._execute_query("INSERT INTO Списания_товаров (СотрудникID, Причина) VALUES (?, ?)", (data["sotrudnik_id"], data["prichina"]), commit=True, get_last_rowid=True)
                if s_id: QMessageBox.information(self, "Успех", f"Списание (ID: {s_id}) оформлено (упрощенно)."); self.load_data_into_table("Списания товаров")

    def update_report_params_ui(self):
        report_name = self.comboBox_ReportType.currentText()
        current_period_type_widget = self.current_report_param_widgets.get("period_type")
        selected_period_type = current_period_type_widget.currentText() if current_period_type_widget else None
        for i in reversed(range(self.formLayout_ReportParams.count())): 
            item = self.formLayout_ReportParams.itemAt(i)
            if item.widget(): item.widget().deleteLater()
            elif item.layout():
                layout_to_remove = item.layout()
                while layout_to_remove.count():
                    child_item = layout_to_remove.takeAt(0)
                    if child_item.widget(): child_item.widget().deleteLater()
                layout_to_remove.deleteLater()
        self.current_report_param_widgets.clear()
        if report_name != "Анализ продаж за период": self.textEdit_ReportOutput.clear()
        if not report_name or report_name not in self.reports_definitions: return
        report_config = self.reports_definitions[report_name]
        if report_name != "Анализ продаж за период": selected_period_type = None
        for param_info in report_config.get("params", []):
            param_name = param_info["name"]
            if param_name == "period_type" and selected_period_type is None: selected_period_type = param_info.get("default", "month")
            if report_name == "Анализ продаж за период":
                visible_on_rules = param_info.get("visible_on")
                if visible_on_rules and selected_period_type not in visible_on_rules: continue
            label_text = param_info["label"]; widget_type = param_info["widget_type"]; widget = widget_type(self)
            if isinstance(widget, QSpinBox):
                widget.setMinimum(param_info.get("min", 0)); widget.setMaximum(param_info.get("max", 2099 if param_name == "year" else 99999))
                default_val = param_info.get("default")
                if default_val is None and param_name == "year": default_val = QDate.currentDate().year()
                elif default_val is None and param_name == "month_number": default_val = QDate.currentDate().month()
                elif default_val is None and param_name == "week_number": default_val = QDate.currentDate().weekNumber()[0]
                widget.setValue(default_val if default_val is not None else 0)
            elif isinstance(widget, QLineEdit): widget.setPlaceholderText(param_info.get("placeholder", ""));  widget.setText(str(param_info.get("default","")))
            elif isinstance(widget, QDateEdit): widget.setCalendarPopup(True); widget.setDisplayFormat("yyyy-MM-dd"); widget.setDate(QDate.currentDate().addDays(param_info.get("default_offset_days", 0)))
            elif isinstance(widget, QComboBox) and param_name == "period_type":
                widget.addItems(param_info.get("options", []))
                current_val_to_set = selected_period_type if selected_period_type else param_info.get("default", "month")
                widget.blockSignals(True); widget.setCurrentText(current_val_to_set); widget.blockSignals(False)
                if param_info.get("triggers_update"): widget.currentTextChanged.connect(self.update_report_params_ui)
            self.formLayout_ReportParams.addRow(QLabel(label_text), widget); self.current_report_param_widgets[param_name] = widget

    def run_selected_report(self):
        report_name = self.comboBox_ReportType.currentText()
        if not report_name or report_name not in self.reports_definitions: QMessageBox.warning(self, "Ошибка", "Тип отчета не выбран."); return
        report_config = self.reports_definitions[report_name]; report_function = report_config["function"]; params_for_function = {}
        try:
            current_period_type = self.current_report_param_widgets.get("period_type", None)
            if current_period_type: current_period_type = current_period_type.currentText()
            for param_info in report_config.get("params", []):
                param_name = param_info["name"]
                if report_name == "Анализ продаж за период":
                    visible_on_rules = param_info.get("visible_on")
                    if visible_on_rules and current_period_type not in visible_on_rules: continue
                if param_name not in self.current_report_param_widgets: continue
                widget = self.current_report_param_widgets[param_name]; value = None
                if isinstance(widget, QSpinBox): value = widget.value()
                elif isinstance(widget, QLineEdit):
                    value = widget.text()
                    if param_name == "product_id":
                        if not value: QMessageBox.warning(self, "Ошибка", "ID Товара пуст."); return
                        if not value.isdigit(): QMessageBox.warning(self, "Ошибка", "ID Товара число."); return
                        value = int(value)
                elif isinstance(widget, QDateEdit): value = widget.date().toString(Qt.ISODate)
                elif isinstance(widget, QComboBox): value = widget.currentText()
                if report_name == "Анализ продаж за период":
                    if param_name == "period_type": params_for_function["period_type"] = value
                    elif param_name == "specific_date": params_for_function["specific_date"] = value
                    elif param_name == "year": params_for_function["year"] = value
                    elif param_name == "week_number": params_for_function["week_or_month_number"] = value
                    elif param_name == "month_number": params_for_function["week_or_month_number"] = value
                else: params_for_function[param_name] = value
            if report_name == "Анализ продаж за период":
                pt = params_for_function.get("period_type")
                if pt == "day": params_for_function.pop("year", None); params_for_function.pop("week_or_month_number", None)
                elif pt == "week": params_for_function.pop("specific_date", None)
                elif pt == "month": params_for_function.pop("specific_date", None)
        except KeyError as e: QMessageBox.critical(self, "Ошибка", f"Сбор параметров (KeyError): {e}."); return
        except ValueError as e: QMessageBox.critical(self, "Ошибка", f"Неверный формат: {e}."); return
        self.textEdit_ReportOutput.setText("Формирование..."); QApplication.processEvents()
        try:
            headers, data_rows = report_function(**params_for_function)
            if headers and data_rows:
                if headers == ["Ошибка"] and isinstance(data_rows[0], tuple) and len(data_rows[0]) > 0 : self.textEdit_ReportOutput.setText(data_rows[0][0])
                else: self.textEdit_ReportOutput.setText(tabulate(data_rows, headers=headers, tablefmt="grid"))
            elif headers: self.textEdit_ReportOutput.setText(tabulate([], headers=headers, tablefmt="grid") + "\n\n(Нет данных)")
            else: self.textEdit_ReportOutput.setText("Не удалось сформировать отчет или нет данных.")
        except Exception as e: self.textEdit_ReportOutput.setText(f"Ошибка: {e}"); QMessageBox.critical(self, "Ошибка", f"Ошибка: {e}"); traceback.print_exc()

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False, commit=False, get_last_rowid=False):
        conn = None
        try:
            conn = sqlite3.connect(self.DB_NAME); cursor = conn.cursor(); cursor.execute(query, params or ())
            if commit: conn.commit()
            if fetch_one: return cursor.fetchone()
            if fetch_all: return cursor.fetchall()
            if get_last_rowid and commit and cursor.lastrowid: return cursor.lastrowid
            if commit: return True
            return True
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка БД", f"{e}\nЗапрос: {query}\nПараметры: {params}"); print(f"DB Error: {e}\nQuery: {query}\nParams: {params}")
            return None
        finally:
            if conn: conn.close()

def run_application():
    app = QApplication(sys.argv); print("Инициализация БД...")
    BD.init_db()
    conn_check = None; should_add_data = False
    try:
        conn_check = sqlite3.connect(PharmacyApp.DB_NAME); cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT COUNT(*) FROM Поставщики")
        if cursor_check.fetchone()[0] == 0: should_add_data = True; print("Таблица 'Поставщики' пуста. Добавление данных.")
        else: print("В БД есть данные ('Поставщики'). Данные не добавляются.")
    except sqlite3.Error as e: print(f"Ошибка проверки БД ({e}). Добавление данных."); should_add_data = True
    finally:
        if conn_check: conn_check.close()
    if should_add_data:
        try: print("Добавление данных..."); data.add_test_data(); print("Данные добавлены.")
        except sqlite3.IntegrityError as e: print(f"Ошибка целостности: {e}")
        except Exception as e: print(f"Ошибка добавления данных: {e}"); traceback.print_exc()

    
    window = PharmacyApp(); window.show(); sys.exit(app.exec_())

if __name__ == '__main__':
    run_application()