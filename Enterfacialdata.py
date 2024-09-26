import sys
import os
import pickle
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel
import cv2

class FaceDatabaseCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.mtcnn = MTCNN(image_size=160)
        self.resnet = InceptionResnetV1(pretrained='vggface2').eval()
        self.face_database = {}
        self.load_database()

    def initUI(self):
        self.setWindowTitle('Face Feature Database Creator')
        layout = QVBoxLayout()

        self.label = QLabel('Click "Load Images" to upload images of a person.')
        layout.addWidget(self.label)

        btnLoad = QPushButton('Load Images', self)
        btnLoad.clicked.connect(self.load_images)
        layout.addWidget(btnLoad)

        btnSave = QPushButton('Save Features', self)
        btnSave.clicked.connect(self.save_features)
        layout.addWidget(btnSave)

        self.setLayout(layout)

    def load_images(self):
        fname = QFileDialog.getOpenFileNames(self, 'Open file', '/home', "Image files (*.jpg *.jpeg *.png)")
        self.image_files = fname[0]
        if self.image_files:
            self.label.setText(f'{len(self.image_files)} images loaded.')

    def extract_features(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        boxes, _ = self.mtcnn.detect(img)
        if boxes is not None:
            face = img[int(boxes[0][1]):int(boxes[0][3]), int(boxes[0][0]):int(boxes[0][2])]
            face_tensor = self.mtcnn(face)
            face_encoding = self.resnet(face_tensor.unsqueeze(0))
            return face_encoding
        return None

    def save_features(self):
        features = []
        person_id = os.path.basename(self.image_files[0])  # Assuming the file name can be used as an ID.
        for path in self.image_files:
            feature = self.extract_features(path)
            if feature is not None:
                features.append(feature.detach().numpy())
        self.face_database[person_id] = features
        with open('face_data.pkl', 'wb') as db_file:
            pickle.dump(self.face_database, db_file)
        self.label.setText('Features saved to face_data.pkl.')

    def load_database(self):
        try:
            with open('face_data.pkl', 'rb') as db_file:
                self.face_database = pickle.load(db_file)
        except FileNotFoundError:
            self.face_database = {}

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FaceDatabaseCreator()
    ex.show()
    sys.exit(app.exec_())
