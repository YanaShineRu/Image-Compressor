import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QFileDialog, QMessageBox, QProgressBar, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt
from PIL import Image
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
        self.error_log = []

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
            self.error_count = 0
            self.error_log = []
            for root, _, files in os.walk(self.directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                        self.files.append(file_path)

            if self.files:
                self.current_file = 0
                self.progress_bar.setMaximum(len(self.files))
                self.progress_label.setText(f'Обработано файлов {self.current_file + 1}/{len(self.files)}')

                self.process_next_file()
            else:
                QMessageBox.warning(self, 'Ошибка', 'В выбранной директории нет изображений.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Директория не выбрана.')

    def process_next_file(self):
        file_path = self.files[self.current_file]
        try:
            image = Image.open(file_path)
            image.save(file_path, optimize=True, quality=self.quality)
        except Exception as e:
            print(f"Ошибка при обработке файла: {file_path}")
            print(f"Ошибка: {e}")
            self.error_count += 1
            self.error_log.append((file_path, str(e)))

        self.current_file += 1
        self.progress_bar.setValue(self.current_file)
        self.progress_label.setText(f'Сжатие файла {self.current_file}/{len(self.files)}')

        if self.current_file < len(self.files):
            self.process_next_file()
        else:
            QMessageBox.information(self, 'Готово', 'Сжатие изображений завершено.')

            if self.error_count > 0:
                self.create_error_log_file()

            self.error_label.setText(f'Ошибки обработки: {self.error_count}')

    def create_error_log_file(self):
        error_log_file = os.path.join(self.directory, 'Error.log')
        with open(error_log_file, 'w') as f:
            for file_path, error_message in self.error_log:
                f.write(f'Файл: {file_path}\n')
                f.write(f'Ошибка: {error_message}\n\n')

    def closeEvent(self, event):
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageCompressor()
    window.show()
    sys.exit(app.exec_())
