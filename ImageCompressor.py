import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QFileDialog, QMessageBox, QProgressBar, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QDesktopWidget
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PIL import Image
from tqdm import tqdm

class Worker(QObject):
    finished = pyqtSignal()
    progress_changed = pyqtSignal(int)
    error_occurred = pyqtSignal(str)

    def __init__(self, files, quality):
        super().__init__()
        self.files = files
        self.quality = quality

    def process_files(self):
        for i, file_path in enumerate(self.files):
            try:
                image = Image.open(file_path)
                image.save(file_path, optimize=True, quality=self.quality)
            except Exception as e:
                error_message = f"Ошибка при обработке файла: {file_path}\nОшибка: {str(e)}"
                self.error_occurred.emit(error_message)
            else:
                self.progress_changed.emit(i + 1)

        self.finished.emit()

class ImageCompressor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Image Compressor 1.0.0 | by YanaShine')
        self.setFixedSize(350, 200)
        self.center_window()

        self.directory = None
        self.files = []
        self.quality = 85
        self.error_count = 0
        self.error_log = []

        self.worker = None

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
                self.progress_bar.setMaximum(len(self.files))
                self.progress_label.setText(f'Обработано файлов 0/{len(self.files)}')

                self.worker = Worker(self.files, self.quality)
                self.worker.finished.connect(self.processing_completed)
                self.worker.progress_changed.connect(self.update_progress)
                self.worker.error_occurred.connect(self.handle_error)

                QTimer.singleShot(0, self.worker.process_files)
            else:
                QMessageBox.warning(self, 'Ошибка', 'В выбранной директории нет изображений.')
        else:
            QMessageBox.warning(self, 'Ошибка', 'Директория не выбрана.')

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        self.progress_label.setText(f'Обработано файлов {value}/{len(self.files)}')

    def handle_error(self, error_message):
        print(error_message)
        self.error_count += 1
        self.error_log.append(error_message)

    def processing_completed(self):
        QMessageBox.information(self, 'Готово', 'Сжатие изображений завершено.')

        if self.error_count > 0:
            self.create_error_log_file()

        self.error_label.setText(f'<font color="red">Ошибки обработки: {self.error_count}</font>')

    def create_error_log_file(self):
        error_log_file = os.path.join(self.directory, 'Error.log')
        with open(error_log_file, 'w') as f:
            for error_message in self.error_log:
                f.write(error_message)
                f.write('\n')

    def closeEvent(self, event):
        if self.worker is not None:
            self.worker.finished.disconnect()
            self.worker.progress_changed.disconnect()
            self.worker.error_occurred.disconnect()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageCompressor()
    window.show()
    sys.exit(app.exec_())
