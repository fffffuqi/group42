import sqlite3

class UserModel:
    @staticmethod
    def get_user_by_id(userid):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\user.db')
        cursor = conn.cursor()
        cursor.execute("SELECT userid, password FROM users WHERE userid=?", (userid,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def create_user(userid, password):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\user.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (userid, password, authentic, auntheninfo, online) VALUES (?, ?, ?, ?, ?)",
                       (userid, password, False, None, False))
        conn.commit()
        conn.close()

    @staticmethod
    def set_user_online(userid, online_status):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\user.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET online=? WHERE userid=?", (online_status, userid))
        conn.commit()
        conn.close()

    @staticmethod
    def set_all_users_offline():
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\user.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET online=? WHERE online=?", (False, True))
        conn.commit()
        conn.close()

    @staticmethod
    def get_online_user():
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\user.db')
        cursor = conn.cursor()
        cursor.execute("SELECT userid, authentic FROM users WHERE online=?", (True,))
        user = cursor.fetchone()
        conn.close()
        return user

    @staticmethod
    def get_users_by_page(page_num, page_size):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\user.db')
        cursor = conn.cursor()
        offset = (page_num - 1) * page_size
        cursor.execute("SELECT userid, password, authentic, auntheninfo, online FROM users LIMIT ? OFFSET ?", (page_size, offset))
        users = cursor.fetchall()
        conn.close()
        return users

    @staticmethod
    def update_user(userid, field, value):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\user.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {field}=? WHERE userid=?", (value, userid))
        conn.commit()
        conn.close()

class EnvironmentModel:
    @staticmethod
    def get_data_by_page(page_num, page_size):
        try:
            offset = (page_num - 1) * page_size
            conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\analyse.db')
            cursor = conn.cursor()
            cursor.execute("SELECT time, temperature, lighting, Doorswitch, Windowswitch FROM analyse LIMIT ? OFFSET ?", (page_size, offset))
            data = cursor.fetchall()
            conn.close()
            return data
        except Exception as e:
            print(f"Error reading environment data: {e}")
            return []

    @staticmethod
    def update_data(time, field, value):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\analyse.db')
        cursor = conn.cursor()
        cursor.execute(f"UPDATE analyse SET {field}=? WHERE time=?", (value, time))
        conn.commit()
        conn.close()

class DeviceStateModel:
    @staticmethod
    def create_tables():
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\device_state.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS device_state (
                            id INTEGER PRIMARY KEY,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            device TEXT,
                            state TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS temperature (
                            id INTEGER PRIMARY KEY,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            temperature REAL,
                            humidity REAL)''')
        conn.commit()
        conn.close()

    @staticmethod
    def log_device_state(device, state):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\device_state.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO device_state (device, state) VALUES (?, ?)", (device, state))
        conn.commit()
        conn.close()

    @staticmethod
    def log_temperature(temperature, humidity):
        conn = sqlite3.connect('C:\\Users\\17590\\PycharmProjects\\onnxcaffe\\database\\device_state.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO temperature (temperature, humidity) VALUES (?, ?)", (temperature, humidity))
        conn.commit()
        conn.close()
