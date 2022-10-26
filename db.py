import sqlite3
import gspread


def db_update(inf_4=None):
    with sqlite3.connect('klinni_base.db') as con:
        cur = con.cursor()
        if inf_4 is None:
            gc = gspread.service_account(filename='testbot-365118-7a5c7350796d.json')
            sh = gc.open("Клинни")

            worksheet = sh.get_worksheet(0)
            list_of_lists = worksheet.get_all_values()
            inf = tuple([1] + list_of_lists[1])
            cur.execute("""CREATE TABLE IF NOT EXISTS klinni_inf(
            id INTEGER,
            check_list TEXT,
            title TEXT,
            description TEXT,
            how_work TEXT,
            general_information TEXT,
            после_ремонта TEXT,
            сайт TEXT,
            цены TEXT,
            время TEXT);
            """)

            worksheet = sh.get_worksheet(1)
            list_of_lists = worksheet.get_all_values()
            inf_2 = [tuple([1] + i) for i in list_of_lists]
            cur.execute("DELETE FROM klinni_inf")
            cur.execute("INSERT INTO klinni_inf VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", inf)

            cur.execute("""CREATE TABLE IF NOT EXISTS cleaners(
                    id INTEGER,
                    name TEXT,
                    name_inf TEXT,
                    inf TEXT,
                    photo TEXT);
                    """)

            worksheet = sh.get_worksheet(2)
            list_of_lists = worksheet.get_all_values()
            inf_3 = [tuple([1] + i) for i in list_of_lists[1:]]
            cur.execute("DELETE FROM cleaners")
            cur.executemany("INSERT INTO cleaners VALUES(?, ?, ?, ?, ?);", inf_2)

            cur.execute("""CREATE TABLE IF NOT EXISTS additional(
                id TEXT,
                additional_services TEXT,
                количество TEXT,
                Цена INTEGER,
                time INTEGER);
                """)

            cur.execute("DELETE FROM additional")
            cur.executemany("INSERT INTO additional VALUES(?, ?, ?, ?, ?);", inf_3)

        elif inf_4 is not None:
            cur.execute("""CREATE TABLE IF NOT EXISTS user_id(
                        access INTEGER,
                        login TEXT,
                        chat_id INTEGER,
                        address TEXT,
                        full_name TEXT,
                        telephone TEXT,
                        email TEXT);
                        """)
            cur.execute("SELECT * FROM user_id WHERE chat_id=?", (inf_4[1], ))
            res = cur.fetchone()
            print(res)
            cur.execute("DELETE FROM user_id WHERE chat_id=?", (inf_4[1], ))
            if res[0] != 0:
                cur.execute("INSERT INTO user_id VALUES(?, ?, ?, ?, ?, ?, ?);", (res[0], *inf_4))
            else:
                cur.execute("INSERT INTO user_id VALUES(0, ?, ?, ?, ?, ?, ?);", inf_4)