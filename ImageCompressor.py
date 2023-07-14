import os
import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QFileDialog, QMessageBox, QProgressBar, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt
from tqdm import tqdm

class ImageCompressor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Image Compressor 1.0.0 | by YanaShine')
        self.setFixedSize(350, 200)
        self.center_window()

        self.directory = None
        self.files = []
        self.current_file = 0
        self.quality = 85
        self.error_count = 0

        self.init_ui()

    def center_window(self):
        screen_geometry = QDesktopWidget().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def init_ui(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)

        select_button = QPushButton('Выбрeрите директорию', widget)
        select_button.clicked.connect(self.select_directory)

        self.quality_label = QLabel('Степень сжатия: 85', widget)
        self.quality_slider = QSlider(Qt.Horizontal, widget)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(85)
        self.quality_slider.valueChanged.connect(self.update_quality_label)

        compress_button = QPushButton('Выполнить сжатие', widget)
        compress_button.clicked.connect(self.compress_images)

        self.progress_bar = QProgressBar(widget)
        self.progress_label = QLabel('', widget)
        self.error_label = QLabel('', widget)

        counter_layout = QHBoxLayout()
        counter_layout.addWidget(self.progress_label)
        counter_layout.addWidget(self.error_label)

        layout = QVBoxLayout()
        layout.addWidget(select_button)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.quality_slider)
        layout.addWidget(compress_button)
        layout.addWidget(self.progress_bar)
        layout.addLayout(counter_layout)
        widget.setLayout(layout)

    def update_quality_label(self):
        self.quality = 100 - self.quality_slider.value()
        self.quality_label.setText(f'Степень сжатия: {self.quality}')

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, 'Выберите директорию')

    def compress_images(self):
        if self.directory:
            self.files = []
            self.current_file = 0
            self.error_count = 0

            self.scan_directory(self.directory)

            if self.files:
                self.progress_bar.setMaximum(len(self.files))
                self.progress_label.setText(f'Обработано файлов {self.current_file + 1}/{len(self.files)}')

                self.process_files()
            else:
                QMessageBox.warning(self, 'Ошибка', 'В выбранной директории нет изображений.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Директория не выбрана.')

    def scan_directory(self, directory):
        for root, _, files in os.walk(directory):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                self.files.append(file_path)

    def process_files(self):
        for file_path in tqdm(self.files[self.current_file:], desc='Обработка файлов', unit='файл'):
            self.process_file(file_path)
            self.current_file += 1
            self.progress_bar.setValue(self.current_file)
            self.progress_label.setText(f'Сжатие файла {self.current_file}/{len(self.files)}')

        self.processing_completed()

    def process_file(self, file_path):
        try:
            image = cv2.imread(file_path)
            if image is not None:
                cv2.imwrite(file_path, image, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
            else:
                self.write_error_log(file_path, 'Ошибка чтения изображения')
                self.error_count += 1
        except Exception as e:
            self.write_error_log(file_path, str(e))
            self.error_count += 1

    def processing_completed(self):
        QMessageBox.information(self, f'Готово', f'Сжатие изображений завершено.\nОшибок: {self.error_count}')
        self.error_label.setText(f'<font color="red">Ошибки обработки: {self.error_count}</font>')

    def closeEvent(self, event):
        QApplication.quit()

    def write_error_log(self, file_path, error_message):
        log_file_path = os.path.join(self.directory, 'error_log.txt')
        try:
            with open(log_file_path, 'a') as f:
                f.write(f"Ошибка при обработке файла: {file_path}\n")
                f.write(f"Ошибка: {error_message}\n")
                f.write("------------------------\n")
        except Exception as e:
            print(f"Ошибка записи в журнал ошибок: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageCompressor()
    window.show()
    sys.exit(app.exec_())
