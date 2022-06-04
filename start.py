from flask import Flask, flash, render_template, request, g, current_app
import sqlite3, os

app = Flask(__name__)
app.config.update(
    SEND_FILE_MAX_AGE_DEFAULT=0,  # постоянная подгрузка css в браузере
    DATABASE=os.path.join(app.root_path, 'database.db'))  # подключение файла БД


def connect_db():
    """Соединяет с указанной базой данных"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def sql_add(cortege):
    """Добавление записи в БД"""
    db = connect_db()
    db.execute(
        """INSERT INTO PhoneHandlerBook (LastName, FirstName, MiddleName, Phone) VALUES(?, ?, ?, ?)""", cortege)
    db.commit()


def sql_delete(con, id):
    """Удаление записи по ID"""
    cursor = con.cursor()
    rows = sql_out()
    i = 0

    for row in rows:
        if i == id:
            cursor.execute("""DELETE FROM PhoneHandlerBook WHERE Phone=""" + str(row[3]))
            break
        i += 1
    con.commit()


def sql_update(con,id,cortege):
    '''Обновление записи по id'''
    cursor = con.cursor()
    rows = sql_out()
    i = 0

    for row in rows:
        if i == id:
            cursor.execute(f"""UPDATE PhoneHandlerBook SET LastName = ?, FirstName = ?, MiddleName = ?, Phone = ?  Where Phone = {str(row[3])}""", cortege)
            break
        i += 1
    con.commit()

def sql_out():
    """Получение объекта БД с записями"""
    db = connect_db()
    cur = db.execute("""SELECT FirstName, LastName, MiddleName, Phone FROM PhoneHandlerBook ORDER BY FirstName""")
    rows = cur.fetchall()
    return rows


def sql_search(value):
    """Алгоритм поиска"""
    list = []
    for row in sql_out():
        if (row[0].find(value) >= 0) or (row[1].find(value) >= 0) or (row[2].find(value) >= 0) or (
                str(row[3]).find(value) >= 0):
            phone = str(row[3])
            list.append(row[0] + " " + row[1] + " " + row[2] + " " + phone)

    if len(list) == 0:  # если нет совпадений
        list.append("Ничего не найдено!")
        return list
    else:
        return list


def reset_area(data):
    """Обновление переменной с данными"""
    for row in sql_out():
        ind_list = sql_out().index(row)
        ind_list += 1
        data += str(ind_list) + ". " + row[0] + " " + row[1] + " " + row[2] + " "
        phone = str(row[3])
        data += phone + '\n' + "    "
    return data


def len_data():
    """Подсчёт количества записей в БД"""
    name_count = "Количество записей: "
    count = len(sql_out())
    string_count = name_count + str(count)
    return string_count


class Phone(list):
    def add(self, LastName, FirstName, MiddleName, Phone):
        """Добавление строки в объект класса"""
        sql_add((LastName, FirstName, MiddleName, Phone))

    def delete(self, id):
        """Удаление строки по айди"""
        sql_delete(connect_db(), id)

    def update(self, id, LastName, FirstName, MiddleName, Phone):
        sql_update(connect_db(), id, (LastName, FirstName, MiddleName, Phone))


persons = Phone()


@app.route('/', methods=['GET', 'POST'])
def index():
    global last_name, first_name, middle_name, phone, id_num, search_value
    data = ''
    result = ''
    result_count = 'Ничего не найдено'
    count = 'Записей нет'
    if len(sql_out()) != 0:  # проверка наличия записей для счётчика
        string_count = len_data()
    else:
        string_count = count

    data += reset_area(data)

    if request.method == 'POST':
        last_name = request.form.get('last_name')  # запрос к данным input
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        phone = request.form.get('phone')
        id_num = request.form.get('del')
        search_value = request.form.get('search-value')

    if "submit" in request.form:  # если нажата кнопка добавить
        print("Ok")
        data = ''

        persons.add(last_name, first_name, middle_name, phone)

        if len(sql_out()) != 0:
            string_count = len_data()
        else:
            string_count = count

        data += reset_area(data)

    if "submit-del" in request.form:  # если нажата кнопка удаления

        persons.delete(int(id_num) - 1)
        data = ''
        if len(sql_out()) != 0:
            string_count = len_data()
        else:
            string_count = count
        data += reset_area(data)

    if "submit-edit" in request.form: # если нажата кнопка редактирования

        print(id_num, last_name, first_name, middle_name, phone)
        persons.update((int(id_num) - 1), last_name, first_name, middle_name, phone)
        data = ''
        if len(sql_out()) != 0:
            string_count = len_data()
        else:
            string_count = count
        data += reset_area(data)

    if "submit-search" in request.form:  # если нажата кнопка поиска
        list = sql_search(search_value)
        for elem in list:
            result += elem + '\n'
            if elem == "Ничего не найдено!":
                result_count = "Количество совпадений: 0"
                print(result_count)
            else:
                result_count = "Количество совпадений: " + str(len(list))
                data = list

    return render_template('main.html', data=data, count=string_count, result=result, result_count=result_count,
                           users=sql_out())


app.run(debug=True)
