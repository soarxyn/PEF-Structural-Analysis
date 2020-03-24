from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PEF - Análise de Estruturas 2D")
        self.setGeometry(0, 0, 1280, 720)
        self.setWindowIcon(QIcon("EP.jpg"))

        screenRectangle : QtRectangle = self.frameGeometry()
        centerPoint : QtPoint = QDesktopWidget().availableGeometry().center()
        screenRectangle.moveCenter(centerPoint)
        self.move(screenRectangle.topLeft())

        self.background : QImage = QImage(self.size(), QImage.Format_RGB32)
        self.background.fill(Qt.black)

        self.snapPoints : List[SnapPoints] = list()
        
    def mousePressEvent(self, event):
        pass

    def keyPressEvent(self, event):
        pass


if __name__ == "__main__":
    application : QApplication = QApplication([])
    
    window : Window = Window()
    window.show()

    application.exec_()
    