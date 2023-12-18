import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class StartWindow(QWidget):

    def __init__(self, controller):
        QWidget.__init__(self)
        self.controller = controller
        grid = QGridLayout()
        self.setStyleSheet("background-color:#3d4c51;")
        self.setWindowTitle("Start Menu")

        imageBox = QVBoxLayout()
        self.im = QPixmap("./Images/delsys.png")
        self.label = QLabel()
        self.label.setPixmap(self.im)
        self.label.setAlignment(Qt.AlignCenter)
        imageBox.addWidget(self.label)
        imageBox.setAlignment(Qt.AlignBaseline)
        imageBox.setContentsMargins(0,100,0,0)
        grid.addLayout(imageBox, 0, 0)

        errorbox = QHBoxLayout()
        errorbox.setSpacing(0)
        self.error = QLabel()
        self.error.setText("")
        self.error.setAlignment(Qt.AlignHCenter)
        self.error.setStyleSheet('QLabel {color: red;}')
        errorbox.addWidget(self.error)
        errorbox.setAlignment(Qt.AlignRight)
        grid.addLayout(errorbox,1,0)

        buttonBox = QHBoxLayout()
        buttonBox.setSpacing(0)

        button = QPushButton('Connect', self)
        button.setToolTip('Collect Data')
        button.objectName = 'Collect'
        button.clicked.connect(self.Connect_Button_Callback)
        button.setFixedSize(200, 100)
        button.setStyleSheet('QPushButton {color: white;}')
        buttonBox.addWidget(button)

        plotBox = QHBoxLayout()

        plot_label = QLabel('Display Plot')
        plot_label.setStyleSheet('color: white')
        plot_label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        plotBox.addWidget(plot_label)
        self.plot_enabled = QCheckBox()
        plotBox.addWidget(self.plot_enabled)
        plotBox.setAlignment(Qt.AlignHCenter)
        grid.addLayout(buttonBox, 2, 0)
        grid.addLayout(plotBox, 3, 0)

        self.setLayout(grid)
        self.setFixedSize(self.width(), self.height())

    def Connect_Button_Callback(self):
        """Shows the Data Collector GUI window"""
        try:
            self.controller.showCollectData()

        except Exception as e:
            if "product not licensed." in str(e):
                self.error.setText("Error: Key/License Not Validated\nClose the program and paste your key/license into TrignoBase.py file\nContact support@delsys.com if you have not received your APi key/license")
            elif "no RF subsystem found" in str(e):
                self.error.setText("Error: Trigno system not found\nPlease make sure your base station or lite dongle is plugged in via USB\nVisit our website to request a quote or contact support@delsys.com")
            else:
                self.error.setText(str(e))
            self.controller.startWindow.show()
            print(Exception)

