import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    light_count_signal = pyqtSignal(int)  # 新增亮光计数信号

    def __init__(self):
        super().__init__()
        self.run_flag = True

    def run(self):
        cap = cv2.VideoCapture(0)
        while self.run_flag:
            ret, frame = cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                light_count = 0  # 记录亮光簇个数

                for contour in contours:
                    if cv2.contourArea(contour) > 1000:  # 调整面积阈值为1000
                        light_count += 1
                        cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)

                # 发送亮光簇计数
                self.light_count_signal.emit(light_count)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(q_img)

        cap.release()

    def stop(self):
        self.run_flag = False
        self.quit()
        self.wait()

class VideoCapture(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("灯光亮点检测")
        self.setGeometry(100, 100, 800, 600)

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 800, 500)

        self.light_count_label = QLabel(self)  # 显示亮光数的标签
        self.light_count_label.setGeometry(10, 510, 200, 30)
        self.light_count_label.setText("灯光数：0")

        self.button = QPushButton("开始检测", self)
        self.button.setGeometry(350, 550, 100, 40)
        self.button.clicked.connect(self.toggle_detection)

        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.light_count_signal.connect(self.update_light_count)  # 连接信号

        self.is_running = False

    def toggle_detection(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.button.setText("停止检测")
            self.thread.start()
        else:
            self.button.setText("开始检测")
            self.thread.stop()

    def update_image(self, q_img):
        self.label.setPixmap(QPixmap.fromImage(q_img))

    def update_light_count(self, count):
        self.light_count_label.setText(f"灯光数：{count}")  # 更新灯光数显示

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoCapture()
    window.show()
    sys.exit(app.exec_())
