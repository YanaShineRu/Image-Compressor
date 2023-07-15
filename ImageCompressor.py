import os
import sys
import subprocess
import glob
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QFileDialog, QMessageBox, QProgressBar, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt
from PIL import Image
from tqdm import tqdm
from pathlib import Path

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

        select_button = QPushButton('Выберите директорию', widget)
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
        self.quality = self.quality_slider.value()
        self.quality_label.setText(f'Степень сжатия: {self.quality}')

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, 'Выберите директорию')

    def scan_directory(self, directory):
        self.files = []
        file_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        for file_extension in file_extensions:
            pattern = os.path.join(directory, f'**/*{file_extension}')
            files = glob.glob(pattern, recursive=True)
            self.files.extend(files)

    def compress_images(self):
        if self.directory:
            self.files = []
            self.current_file = 0
            self.error_count = 0

            self.scan_directory(self.directory)

            if self.files:
                self.progress_bar.setMaximum(len(self.files))
                self.progress_label.setText(f'Обработано файлов 0/{len(self.files)}')

                self.process_files()
            else:
                QMessageBox.warning(self, 'Ошибка', 'В выбранной директории нет изображений.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Директория не выбрана.')

    def is_supported_image(self, file_path):
        supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        file_extension = Path(file_path).suffix.lower()
        return file_extension in supported_formats

    def process_files(self):
        for file_path in tqdm(self.files, desc='Обработка файлов', unit='файл'):
            self.process_file(file_path)
            self.current_file += 1
            self.progress_bar.setValue(self.current_file)
            self.progress_label.setText(f'Сжатие файла {self.current_file}/{len(self.files)}')

        self.processing_completed()

    def process_file(self, file_path):
        try:
            file_extension = Path(file_path).suffix.lower()

            if file_extension in ['.jpg', '.jpeg']:
                image = Image.open(file_path)
                image.save(file_path, optimize=True, quality=self.quality)
            elif file_extension == '.png':
                image = Image.open(file_path)
                image.save(file_path, optimize=True)
            elif file_extension == '.gif':
                subprocess.run(['gifsicle', '-O3', str(Path(file_path)), '-o', str(Path(file_path))])
            else:
                # Обработка других форматов изображений, если необходимо
                pass
        except Exception as e:
            self.write_error_log(file_path, str(e))
            self.error_count += 1

    def processing_completed(self):
        QMessageBox.information(self, f'Готово', f'Сжатие изображений завершено.\nОшибок: {self.error_count}')
        self.error_label.setText(f'<font color="red">Ошибки обработки: {self.error_count}</font>')

    def closeEvent(self, event):
        QApplication.quit()

    def write_error_log(self, file_path, error_message):
        log_file_path = str(Path(self.directory) / 'error_log.txt')
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
