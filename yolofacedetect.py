import sys
import pickle
import cv2
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer


class FaceRecognizer(QWidget):
    def __init__(self, database_path):
        super().__init__()
        self.database_path = database_path
        self.last_frame = None
        self.initUI()
        self.init_model()
        self.load_database()
        self.start_camera()

    def initUI(self):
        self.setWindowTitle('Face Recognizer')
        self.setGeometry(100, 100, 800, 600)
        self.btnStart = QPushButton('Recognize Face', self)
        self.btnStart.clicked.connect(self.recognize_current_frame)
        self.image_label = QLabel(self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.btnStart)
        layout.addWidget(self.image_label)

    def init_model(self):
        self.mtcnn = MTCNN(image_size=160)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()

    def load_database(self):
        try:
            with open(self.database_path, 'rb') as f:
                self.face_database = pickle.load(f)
        except FileNotFoundError:
            QMessageBox.critical(self, "File Not Found Error", f"The file {self.database_path} does not exist.")
            sys.exit(1)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Unable to access the camera.")
            return
        self.timer = QTimer()
        self.timer.timeout.connect(self.display_video_stream)
        self.timer.start(10)

    def display_video_stream(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, _ = self.mtcnn.detect(frame_rgb)
        if boxes is not None:
            for box in boxes:
                cv2.rectangle(frame_rgb, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        self.last_frame = frame_rgb
        self.image_label.setPixmap(self.convert_cv_qt(frame_rgb))

    def recognize_current_frame(self):
        if self.timer.isActive():
            self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()

        if self.last_frame is not None:
            frame_rgb = np.array(self.last_frame)
            boxes, _ = self.mtcnn.detect(frame_rgb)
            if boxes is not None:
                for box in boxes:
                    face_crop = frame_rgb[int(box[1]):int(box[3]), int(box[0]):int(box[2])]
                    face_tensor = torch.tensor(face_crop).permute(2, 0, 1).unsqueeze(0).float() / 255.
                    encoding = self.resnet(face_tensor)
                    name, similarity = self.recognize(encoding)
                    self.show_message(name, similarity)
            else:
                QMessageBox.information(self, "Recognition Result", "No faces detected.")
        else:
            QMessageBox.critical(self, "Error", "No frame available for recognition.")
        self.start_camera()  # Restart the camera

    def convert_cv_qt(self, cv_img):
        h, w, ch = cv_img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(cv_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(800, 600, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def recognize(self, face_encoding):
        max_similarity = -1
        recognized_name = "Unknown"
        for person_name, db_encodings in self.face_database.items():
            for db_encoding in db_encodings:
                similarity = torch.nn.functional.cosine_similarity(face_encoding, torch.tensor(db_encoding)).item()
                if similarity > max_similarity:
                    max_similarity = similarity
                    recognized_name = person_name if similarity > 0.5 else "Unknown"
        return recognized_name, max_similarity

    def show_message(self, name, similarity):
        msg = QMessageBox()
        msg.setWindowTitle("Recognition Result")
        msg.setText(f"Recognized: {name} (Similarity: {similarity:.2f})" if name != "Unknown" else "Unknown Person")
        msg.exec_()

    def closeEvent(self, event):
        if self.timer.isActive():
            self.timer.stop()
        if self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FaceRecognizer(r'C:\Users\17590\PycharmProjects\onnxcaffe\face_data.pkl')
    ex.show()
    sys.exit(app.exec_())
