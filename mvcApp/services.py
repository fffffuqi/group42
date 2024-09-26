from models import UserModel, EnvironmentModel

import serial
import time

class UserService:
    @staticmethod
    def register_user(username, password, confirm_password):
        if not username or not password or not confirm_password:
            return "Inputs cannot be empty"
        if len(username) > 20 or len(password) > 20:
            return "Inputs too long"
        if password != confirm_password:
            return "Passwords do not match"
        if UserModel.get_user_by_id(username):
            return "Username already exists"
        UserModel.create_user(username, password)
        return "Registration Successful"

    @staticmethod
    def authenticate_user(username, password):
        user = UserModel.get_user_by_id(username)
        if user and user[1] == password:
            UserModel.set_user_online(username, True)
            return True
        return False

    @staticmethod
    def logout_user():
        UserModel.set_all_users_offline()

    @staticmethod
    def get_online_user():
        return UserModel.get_online_user()

    @staticmethod
    def get_users_by_page(page_num, page_size):
        return UserModel.get_users_by_page(page_num, page_size)

    @staticmethod
    def update_user(userid, field, value):
        UserModel.update_user(userid, field, value)

class EnvironmentService:
    @staticmethod
    def get_environment_data_by_page(page_num, page_size):
        return EnvironmentModel.get_data_by_page(page_num, page_size)

    @staticmethod
    def update_environment_data(time, field, value):
        EnvironmentModel.update_data(time, field, value)

class ArduinoService:
    def __init__(self, port, baud_rate=9600):
        self.ser = None
        try:
            self.ser = serial.Serial(port, baud_rate, timeout=1)
            time.sleep(2)  # 等待Arduino重启
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")

    def send_command(self, command, value):
        if self.ser:
            command_str = f"{command} {value}\n"
            self.ser.write(command_str.encode())
            time.sleep(1)  # 等待Arduino处理命令
            response = self.ser.readline().decode().strip()
            return response
        else:
            return "Serial port not initialized or unavailable"

    def read_data(self):
        if self.ser:
            data = self.ser.readline().decode().strip()
            return data
        else:
            return "Serial port not initialized or unavailable"

    def close(self):
        if self.ser:
            self.ser.close()
