import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, \
    QErrorMessage, QMessageBox

from encoding import Decoder, Encoder
from image import Image


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("INFO-F106-L'œil de Yassin")

        # Widgets
        self.load_button = QPushButton("Load image")
        self.load_button.clicked.connect(self.load_image)
        self.save_button = QPushButton("Save image")
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)  # Par défaut, le bouton est désactivé
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.image_label)

        # Widget central
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Variables
        self.image_path = ""

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("ULBMP Files (*.ulbmp)")
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        if file_dialog.exec_():
            self.image_path = file_dialog.selectedFiles()[0]
            try:
                image = Decoder.load_from(self.image_path)
                qimage = self.convert_image_to_qimage(image)
                pixmap = QPixmap.fromImage(qimage)
                self.image_label.setPixmap(pixmap)
                self.save_button.setEnabled(True)  # Activer le bouton de sauvegarde
            except Exception as e:
                error_message = QErrorMessage(self)
                error_message.setWindowTitle("Error Loading Image")
                error_message.showMessage(f"Problem while reading the image: {str(e)}")

    def save_image(self):
        if self.image_path:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "ULBMP Files (*.ulbmp)")
            if save_path:
                try:
                    image = Decoder.load_from(self.image_path)
                    encoder = Encoder(image)
                    encoder.save_to(save_path)
                    QMessageBox.information(self, "Image Saved", "Image saved successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error Saving Image",
                                         f"An error occurred while saving the image: {str(e)}")
        else:
            QMessageBox.warning(self, "No Image Loaded", "No image loaded to save.")

    @staticmethod
    def convert_image_to_qimage(image: Image):
        width = image.width
        height = image.height
        qimage = QImage(width, height, QImage.Format_RGB888)
        for y in range(height):
            for x in range(width):
                pixel = image.pixels[y * width + x]
                r, g, b = pixel.red, pixel.green, pixel.blue
                # Convertir les composantes RGB en int
                r_int, g_int, b_int = int(r), int(g), int(b)
                # Construire une couleur QRgb à partir des composantes RGB
                color = QColor(r_int, g_int, b_int).rgb()
                # Définir la couleur du pixel dans l'image QImage
                qimage.setPixelColor(x, y, QColor(color))
        return qimage

