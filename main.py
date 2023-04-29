from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QDate
from PyQt6 import uic
from datetime import datetime, timedelta
import qdarktheme
import mysql.connector
import configparser
import queries

import gpscripts.gp, gpscripts.mbd, gpscripts.drg, gpscripts.config

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)
        self.read_ini()
        self.logs = []
        self.current_date = datetime.today()
        self.lbl_current_date.setText(self.current_date.strftime('%d/%m/%Y'))
    
        self.db_is_connected = False
        self.log_window_hidden = False

        self.btn_db_connect.clicked.connect(self.db_connect)

        self.btn_update_db_mbd.clicked.connect(self.update_db_mbd)
        self.btn_update_db_gp.clicked.connect(self.update_db_gp)
        self.btn_update_db_drg.clicked.connect(self.update_db_drg)

        self.btn_gp_laura.clicked.connect(lambda: self.toggle_gp_valid("5"))
        self.btn_gp_anton.clicked.connect(lambda: self.toggle_gp_valid("4"))
        self.btn_gp_miranda.clicked.connect(lambda: self.toggle_gp_valid("3"))
        self.btn_gp_nerea.clicked.connect(lambda: self.toggle_gp_valid("9"))
        self.btn_gp_paula.clicked.connect(lambda: self.toggle_gp_valid("10"))
        self.btn_gp_joaquin.clicked.connect(lambda: self.toggle_gp_valid("1"))
        self.btn_gp_sergio.clicked.connect(lambda: self.toggle_gp_valid("2"))
        self.btn_gp_diego.clicked.connect(lambda: self.toggle_gp_valid("8"))
        self.btn_gp_aina.clicked.connect(lambda: self.toggle_gp_valid("7"))
        self.btn_gp_aitor.clicked.connect(lambda: self.toggle_gp_valid("6"))

        self.btn_show_gp_table.clicked.connect(lambda: self.show_query("SELECT * FROM gpdb.gp"))
        self.btn_show_mbd_table.clicked.connect(lambda: self.show_query("SELECT * FROM gpdb.mbd"))
        self.btn_show_drg_table.clicked.connect(lambda: self.show_query("SELECT * FROM gpdb.drg"))

        self.btn_move_back.clicked.connect(self.move_back)
        self.btn_move_forward.clicked.connect(self.move_forward)

        self.btn_run_query.clicked.connect(lambda: self.show_query(self.line_query.text()))

        self.calendarWidget.clicked[QDate].connect(self.selected_date_in_calendar)

        self.btn_toggle_console.clicked.connect(self.toggle_console)

        self.tableWidget.cellChanged.connect(self.update_database_from_table)

        self.run_at_start()

    def run_at_start(self):
        if config["DATABASE"]["auto_connect"] == "True":
            self.db_connect()

        if config["GP-MANAGER"]["run_initial_query"] == "True":
            self.show_query(queries.initial_query)

    def read_ini(self):
        global config
        config = configparser.ConfigParser()
        config.read("config.ini")

    def toggle_console(self):
        if self.log_window_hidden:
            self.log_window.setHidden(False)
            self.log_window_hidden = False
        else:
            self.log_window.setHidden(True)
            self.log_window_hidden = True

    def run_query(self, query, fetch="one"):
        mycursor = mydb.cursor()
        mycursor.execute(query)

        try:
            if fetch == "one":
                result = mycursor.fetchone()
                mydb.commit()
                return result
            if fetch == "all":
                result = mycursor.fetchall()
                mydb.commit()
                return result
        except Exception as e:
            self.log(e)
    
    def show_query(self, query):
        try:
            mycursor = mydb.cursor()
            mycursor.execute(query)
            rows = mycursor.fetchall()

            column_names = [i[0] for i in mycursor.description]

            self.tableWidget.setRowCount(len(rows))
            self.tableWidget.setColumnCount(len(rows[0]))

            self.tableWidget.setHorizontalHeaderLabels(column_names)

            for i, row in enumerate(rows):
                for j, col in enumerate(row):
                    item = QTableWidgetItem(str(col))
                    self.tableWidget.setItem(i, j, item)

            try:
                self.tableWidget.show()
                #self.log(query)
            except:
                pass
        
        except Exception as e:
            self.log(str(e))    

    def log(self, text, show_in_console=False):
        self.logs.append(text + "\n")
        self.update()
        print(text)
    
        with open("log.txt", "a", encoding="utf-8") as log:
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            log.write("[" + dt_string + "]" + " " + text + "\n")

    #Modificar base de datos desde la tabla
    def update_database_from_table(self, row, column):
        if self.chk_edit_table.isChecked():
            item = self.tableWidget.item(row, column)
            new_value = item.text()
            primary_key_item = self.tableWidget.item(row, 0)
            primary_key_value = primary_key_item.text()

            header_item = self.tableWidget.horizontalHeaderItem(column)
            column_name = header_item.text()

            mycursor = mydb.cursor()
            mycursor.execute(f"UPDATE gpdb.gp SET {column_name} = '{new_value}' WHERE gp_id = {primary_key_value}")
            mydb.commit()

            self.chk_edit_table.setChecked(False)
            self.update()
            self.log("Base de datos modificada " + "(" + column_name + ")")

    def update(self):
        #chequear base de datos
        if self.db_is_connected:
            self.lbl_db_status.setText("🟢 Conectado")
        else:
            self.lbl_db_status.setText("🔴 Desconectado")
        self.log_window.setText("".join(self.logs))

        self.lbl_current_date.setText(self.current_date.strftime('%d/%m/%Y'))

        scrollbar = self.log_window.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

        qdate_obj = QDate(self.current_date.year, self.current_date.month, self.current_date.day)
        self.calendarWidget.setSelectedDate(qdate_obj)

        if config["GP-MANAGER"]["display_gp_button_colors"] == "True":
            # ACTUALIZAR BOTONES GP
            current_date = self.current_date.strftime('%Y-%m-%d')

            #joaquin
            gp_id_joaquin = self.get_gp_id_by_player_and_date(1, current_date)
            if gp_id_joaquin:
                if len(gp_id_joaquin) == 1:
                    if self.is_this_gp_valid(gp_id_joaquin[0][0]) == True:
                        self.btn_gp_joaquin.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_joaquin[0][0]) == False:
                        self.btn_gp_joaquin.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_joaquin[0][0]) == "?":
                        self.btn_gp_joaquin.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_joaquin.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_joaquin.setStyleSheet("")

            #sergio
            gp_id_sergio = self.get_gp_id_by_player_and_date(2, current_date)
            if gp_id_sergio:
                if len(gp_id_sergio) == 1:
                    if self.is_this_gp_valid(gp_id_sergio[0][0]) == True:
                        self.btn_gp_sergio.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_sergio[0][0]) == False:
                        self.btn_gp_sergio.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_sergio[0][0]) == "?":
                        self.btn_gp_sergio.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_sergio.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_sergio.setStyleSheet("")

            #miranda
            gp_id_miranda = self.get_gp_id_by_player_and_date(3, current_date)
            if gp_id_miranda:
                if len(gp_id_miranda) == 1:
                    if self.is_this_gp_valid(gp_id_miranda[0][0]) == True:
                        self.btn_gp_miranda.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_miranda[0][0]) == False:
                        self.btn_gp_miranda.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_miranda[0][0]) == "?":
                        self.btn_gp_miranda.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_miranda.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_miranda.setStyleSheet("")

            #anton
            gp_id_anton = self.get_gp_id_by_player_and_date(4, current_date)
            if gp_id_anton:
                if len(gp_id_anton) == 1:
                    if self.is_this_gp_valid(gp_id_anton[0][0]) == True:
                        self.btn_gp_anton.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_anton[0][0]) == False:
                        self.btn_gp_anton.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_anton[0][0]) == "?":
                        self.btn_gp_anton.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_anton.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_anton.setStyleSheet("")

            #laura
            gp_id_laura = self.get_gp_id_by_player_and_date(5, current_date)
            if gp_id_laura:
                if len(gp_id_laura) == 1:
                    if self.is_this_gp_valid(gp_id_laura[0][0]) == True:
                        self.btn_gp_laura.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_laura[0][0]) == False:
                        self.btn_gp_laura.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_laura[0][0]) == "?":
                        self.btn_gp_laura.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_laura.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_laura.setStyleSheet("")

            #aitor
            gp_id_aitor = self.get_gp_id_by_player_and_date(6, current_date)
            if gp_id_aitor:
                if len(gp_id_aitor) == 1:
                    if self.is_this_gp_valid(gp_id_aitor[0][0]) == True:
                        self.btn_gp_aitor.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_aitor[0][0]) == False:
                        self.btn_gp_aitor.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_aitor[0][0]) == "?":
                        self.btn_gp_aitor.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_aitor.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_aitor.setStyleSheet("")

            #aina
            gp_id_aina = self.get_gp_id_by_player_and_date(7, current_date)
            if gp_id_aina:
                if len(gp_id_aina) == 1:
                    if self.is_this_gp_valid(gp_id_aina[0][0]) == True:
                        self.btn_gp_aina.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_aina[0][0]) == False:
                        self.btn_gp_aina.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_aina[0][0]) == "?":
                        self.btn_gp_aina.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_aina.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_aina.setStyleSheet("")

            #diego
            gp_id_diego = self.get_gp_id_by_player_and_date(8, current_date)
            if gp_id_diego:
                if len(gp_id_diego) == 1:
                    if self.is_this_gp_valid(gp_id_diego[0][0]) == True:
                        self.btn_gp_diego.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_diego[0][0]) == False:
                        self.btn_gp_diego.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_diego[0][0]) == "?":
                        self.btn_gp_diego.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_diego.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_diego.setStyleSheet("")

            #nerea
            gp_id_nerea = self.get_gp_id_by_player_and_date(9, current_date)
            if gp_id_nerea:
                if len(gp_id_nerea) == 1:
                    if self.is_this_gp_valid(gp_id_nerea[0][0]) == True:
                        self.btn_gp_nerea.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_nerea[0][0]) == False:
                        self.btn_gp_nerea.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_nerea[0][0]) == "?":
                        self.btn_gp_nerea.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_nerea.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_nerea.setStyleSheet("")

            #paula
            gp_id_paula = self.get_gp_id_by_player_and_date(10, current_date)
            if gp_id_paula:
                if len(gp_id_paula) == 1:
                    if self.is_this_gp_valid(gp_id_paula[0][0]) == True:
                        self.btn_gp_paula.setStyleSheet("background-color : green")
                    if self.is_this_gp_valid(gp_id_paula[0][0]) == False:
                        self.btn_gp_paula.setStyleSheet("background-color : red")
                    if self.is_this_gp_valid(gp_id_paula[0][0]) == "?":
                        self.btn_gp_paula.setStyleSheet("background-color : purple")
                else:
                    self.btn_gp_paula.setStyleSheet("background-color : orange")
            else:
                self.btn_gp_paula.setStyleSheet("")

    def db_full_update(self):
        # actualizar todo y rellenar ids.
        self.update_db_mbd
        self.update_db_gp

    def db_connect(self):
        if config["DATABASE"]["use_default"]:
            host = config["DATABASE"]["host"]
            user = config["DATABASE"]["user"]
            password = config["DATABASE"]["password"]
        else:
            host = self.line_host.text()
            user = self.line_user.text()
            password = self.line_password.text()

        global mydb
        try:
            mydb = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )

            self.db_is_connected = True
            self.log("Base de datos conectada" + " (" + user + ", " + host + ")")
        except:
            self.db_is_connected = False
            self.log("No se ha podido conectar a la base de datos" + " (" + user + ", " + host + ")")

        self.update()

    def update_db_gp(self, date_from=""):
        gp_messages = gpscripts.gp.read_txt()

        for message in gp_messages:
            date_and_time = message[0].split(", ")

            msg_date = date_and_time[0]
            msg_time = date_and_time[1]
            msg_player = message[1] 
            
            # horrible
            if msg_player == "Joaquin":
                msg_player = 1
            if msg_player == "Sergio":
                msg_player = 2
            if msg_player == "Miranda":
                msg_player = 3
            if msg_player == "Anton":
                msg_player = 4
            if msg_player == "Laura":
                msg_player = 5
            if msg_player == "Aitor":
                msg_player = 6
            if msg_player == "Aina":
                msg_player = 7
            if msg_player == "Diego":
                msg_player = 8
            if msg_player == "Nerea":
                msg_player = 9
            if msg_player == "Paula":
                msg_player = 10

            msg_message = message[2]

            date_obj = datetime.strptime(msg_date, '%d/%m/%y')
            msg_date = date_obj.strftime('%Y-%m-%d')

            if self.db_is_connected:
                try:
                    mycursor = mydb.cursor()
                    mycursor.execute(f"INSERT INTO `gpdb`.`gp` (`jugador_id`, `dia`, `hora`, `mensaje`) VALUES ('{msg_player}', '{msg_date}', '{msg_time}', '{msg_message}')")
                    mydb.commit()
                except Exception as e:
                    self.log(str(e))
            else:
                self.log("ERROR: Base de datos no conectada")
                break
            
            # ACTUALIZAR IDs
            mycursor = mydb.cursor()
            mycursor.execute("UPDATE `gpdb`.`gp` JOIN `gpdb`.`mbd` ON `gpdb`.`gp`.dia = `gpdb`.`mbd`.dia SET `gpdb`.`gp`.mbd_id = `gpdb`.`mbd`.mbd_id")
            mydb.commit()
            self.update()
            
        self.log("Finalizado")
        
    def update_db_mbd(self, date_from=""):
        mbd_messages = gpscripts.mbd.read_txt()

        for message in mbd_messages:
            date_and_time = message[0].split(", ")

            msg_date = date_and_time[0]
            msg_time = date_and_time[1]
            msg_player = message[1] # irrelevante, siempre es pablo...
            msg_message = message[2]

            date_obj = datetime.strptime(msg_date, '%d/%m/%y')
            msg_date = date_obj.strftime('%Y-%m-%d')

            self.log(msg_message)

            if self.db_is_connected:
                try:
                    mycursor = mydb.cursor()
                    mycursor.execute("INSERT INTO `gpdb`.`mbd` (`dia`, `hora`, `mensaje`) VALUES (%s, %s, %s);", (msg_date, msg_time, msg_message))
                    mydb.commit()
                except Exception as e:
                    print(e)   
            else:
                self.log("ERROR: Base de datos no conectada")

        self.log("Finalizado")

    def update_db_drg(self, date_from=""):
        drg_messages = gpscripts.drg.read_txt()

        for message in drg_messages:
            date_and_time = message[0].split(", ")

            msg_date = date_and_time[0]
            msg_time = date_and_time[1]
            msg_player = message[1] # irrelevante, siempre es pablo...
            msg_message = message[2]

            date_obj = datetime.strptime(msg_date, '%d/%m/%y')
            msg_date = date_obj.strftime('%Y-%m-%d')

            self.log(msg_message)

            if self.db_is_connected:
                try:
                    mycursor = mydb.cursor()
                    mycursor.execute("INSERT INTO `gpdb`.`drg` (`dia`, `hora`) VALUES (%s, %s);", (msg_date, msg_time))
                    mydb.commit()
                except Exception as e:
                    print(e)   
            else:
                self.log("ERROR: Base de datos no conectada")

        self.log("Finalizado")

    def move_back(self):
        self.current_date -= timedelta(days=1)
        self.move_table()
        self.update()

    def move_forward(self):
        self.current_date += timedelta(days=1)
        self.move_table()
        self.update()

    #Poner la tabla al dia seleccionado
    def move_table(self):
        if self.chk_move_table.isChecked():
            current_date = self.current_date.strftime('%Y-%m-%d')
            self.show_query("SELECT gpdb.gp.gp_id, jugadores.nombre, gpdb.gp.dia, gpdb.gp.hora, gpdb.gp.mbd_id, gpdb.gp.mensaje, gpdb.gp.valido, gpdb.gp.gpv FROM gpdb.gp JOIN gpdb.jugadores ON gpdb.gp.jugador_id = jugadores.jugador_id WHERE DATE(gpdb.gp.dia) = '" + str(current_date) + "' ORDER BY gpdb.gp.gp_id ASC")
            self.update()

    def selected_date_in_calendar(self, date):
        date_str = date.toString('yyyy-MM-dd')
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        self.current_date = date_obj
        self.move_table()
        self.update()

    def get_gp_id_by_player_and_date(self, jugador_id, date):
        query = "SELECT gpdb.gp.gp_id FROM gpdb.gp WHERE gpdb.gp.jugador_id =" + str(jugador_id) + " AND gpdb.gp.dia = '" + str(date) + "'"
        try:
            query_response = self.run_query(query, fetch="all")
            return query_response
        except:
            pass

    def is_this_gp_valid(self, gp_id):
        query = "SELECT gpdb.gp.valido FROM gpdb.gp WHERE gpdb.gp.gp_id =" + str(gp_id)
        try:
            query_response = self.run_query(query)
        except Exception as e:
            return False
        
        if  str(query_response[0]) == "None":
            return "?"
        if "Si" in str(query_response):
            #print("si")
            return True
        if "No" in str(query_response):
            #print("no")
            return False
        else:
            print("else")
            return False


    def toggle_gp_valid(self, player_id):

        current_date = self.current_date.strftime('%Y-%m-%d')
        query = "SELECT gpdb.gp.valido FROM gpdb.gp WHERE gpdb.gp.dia = '" + current_date + "' AND gpdb.gp.jugador_id = " + player_id

        query_response = self.run_query(query)
        
        #buscar gp_id dando el player_id
        try:
            gp_id = self.run_query("SELECT gp_id FROM gpdb.gp WHERE gpdb.gp.dia = '" + current_date + "' AND gpdb.gp.jugador_id = " + player_id)[0]

            if "Si" in str(query_response):
                self.run_query("UPDATE gpdb.gp SET gpdb.gp.valido='No' WHERE gpdb.gp.gp_id=" + str(gp_id))
            if "No" in str(query_response):
                self.run_query("UPDATE gpdb.gp SET gpdb.gp.valido='Si' WHERE gpdb.gp.gp_id=" + str(gp_id))
            if "None" in str(query_response):
                self.run_query("UPDATE gpdb.gp SET gpdb.gp.valido='Si' WHERE gpdb.gp.gp_id=" + str(gp_id))

        except TypeError as e:
            #self.log(str(e))
            self.log("Estás intentando validar un GP no existente")



        self.move_table()
        self.update()

app = QApplication([])
app.setStyle("Fusion")
qdarktheme.setup_theme()
window = UI()
window.show()
app.exec()