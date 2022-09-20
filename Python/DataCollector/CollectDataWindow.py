"""
Data Collector GUI
This is the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from DataCollector.CollectDataController import *
import tkinter as tk
from tkinter import filedialog
from Plotter import GenericPlot as gp

class CollectDataWindow(QWidget):
    def __init__(self,controller):
        QWidget.__init__(self)
        self.pipelinetext = "Off"
        self.controller = controller
        self.buttonPanel = self.ButtonPanel()
        self.plotPanel = self.Plotter()
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.buttonPanel)
        self.splitter.addWidget(self.plotPanel)
        layout = QHBoxLayout()
        self.setStyleSheet("background-color:#3d4c51;")
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        self.setWindowTitle("Collect Data GUI")

        #---- Connect the controller to the GUI
        self.CallbackConnector = PlottingManagement(self.plotCanvas)


    #-----------------------------------------------------------------------
    #---- GUI Components
    def ButtonPanel(self):
        buttonPanel = QWidget()
        buttonLayout = QVBoxLayout()

        self.pipelinelabel = QLabel('Pipeline State', self)
        self.pipelinelabel.setAlignment(Qt.AlignCenter)
        self.pipelinelabel.setStyleSheet("color:white")
        buttonLayout.addWidget(self.pipelinelabel)

        self.pipelinestatelabel = QLabel(self.pipelinetext, self)
        self.pipelinestatelabel.setAlignment(Qt.AlignCenter)
        self.pipelinestatelabel.setStyleSheet("color:white")
        buttonLayout.addWidget(self.pipelinestatelabel)

        #---- Connect Button
        self.connect_button = QPushButton('Connect', self)
        self.connect_button.setToolTip('Connect Base')
        self.connect_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.connect_button.objectName = 'Connect'
        self.connect_button.clicked.connect(self.connect_callback)
        self.connect_button.setStyleSheet('QPushButton {color: white;}')
        buttonLayout.addWidget(self.connect_button)

        findSensor_layout = QHBoxLayout()

        #---- Pair Button
        self.pair_button = QPushButton('Pair', self)
        self.pair_button.setToolTip('Pair Sensors')
        self.pair_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.pair_button.objectName = 'Pair'
        self.pair_button.clicked.connect(self.pair_callback)
        self.pair_button.setStyleSheet('QPushButton {color: white;}')
        self.pair_button.setEnabled(False)
        findSensor_layout.addWidget(self.pair_button)

        #---- Scan Button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.setToolTip('Scan for Sensors')
        self.scan_button.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding)
        self.scan_button.objectName = 'Scan'
        self.scan_button.clicked.connect(self.scan_callback)
        self.scan_button.setStyleSheet('QPushButton {color: white;}')
        self.scan_button.setEnabled(True)
        findSensor_layout.addWidget(self.scan_button)

        buttonLayout.addLayout(findSensor_layout)

        #---- Start Button
        self.start_button = QPushButton('Start', self)
        self.start_button.setToolTip('Start Sensor Stream')
        self.start_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_button.objectName = 'Start'
        self.start_button.clicked.connect(self.start_callback)
        self.start_button.setStyleSheet('QPushButton {color: white;}')
        self.start_button.setEnabled(False)
        buttonLayout.addWidget(self.start_button)

        #---- Stop Button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setToolTip('Stop Sensor Stream')
        self.stop_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stop_button.objectName = 'Stop'
        self.stop_button.clicked.connect(self.stop_callback)
        self.stop_button.setStyleSheet('QPushButton {color: white;}')
        self.stop_button.setEnabled(False)
        buttonLayout.addWidget(self.stop_button)

        #---- Reset Button
        self.reset_button = QPushButton('Reset Pipeline', self)
        self.reset_button.setToolTip('Disarm Pipeline')
        self.reset_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.reset_button.objectName = 'Reset'
        self.reset_button.clicked.connect(self.reset_callback)
        self.reset_button.setStyleSheet('QPushButton {color: white;}')
        self.reset_button.setEnabled(False)
        buttonLayout.addWidget(self.reset_button)

        #---- Drop-down menu of sensor modes
        self.SensorModeList = QComboBox(self)
        self.SensorModeList.setToolTip('Sensor Modes')
        self.SensorModeList.objectName = 'PlaceHolder'
        self.SensorModeList.setStyleSheet('QComboBox {color: white;background: #848482}')
        self.SensorModeList.currentIndexChanged.connect(self.sensorModeList_callback)
        buttonLayout.addWidget(self.SensorModeList)

        #---- List of detected sensors
        self.SensorListBox = QListWidget(self)
        self.SensorListBox.setToolTip('Sensor List')
        self.SensorListBox.objectName = 'PlaceHolder'
        self.SensorListBox.setStyleSheet('QListWidget {color: white;background:#848482}')
        self.SensorListBox.clicked.connect(self.sensorList_callback)
        buttonLayout.addWidget(self.SensorListBox)

        #--- Home Button
        button = QPushButton('Home', self)
        button.setToolTip('Return to Start Menu')
        button.objectName = 'Home'
        button.clicked.connect(self.home_callback)
        button.setStyleSheet('QPushButton {color: white;}')
        buttonLayout.addWidget(button)

        buttonPanel.setLayout(buttonLayout)

        return buttonPanel

    def Plotter(self):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        plot_mode = 'windowed'                 # Select between 'scrolling' and 'windowed'
        pc = gp.GenericPlot(plot_mode)
        pc.native.objectName = 'vispyCanvas'
        pc.native.parent = self
        widget.layout().addWidget(pc.native)
        self.plotCanvas = pc
        return widget

    #-----------------------------------------------------------------------
    #---- Callback Functions
    def getpipelinestate(self):
        self.pipelinetext = self.CallbackConnector.PipelineState_Callback()
        self.pipelinestatelabel.setText(self.pipelinetext)

    def connect_callback(self):
        self.CallbackConnector.Connect_Callback()
        self.connect_button.setEnabled(False)

        self.pair_button.setEnabled(True)
        self.scan_button.setEnabled(True)
        self.getpipelinestate()
        self.pipelinestatelabel.setText(self.pipelinetext + " (Base Connected)")

    def pair_callback(self):
        self.CallbackConnector.Pair_Callback()
        self.scan_callback()
        self.getpipelinestate()

    def scan_callback(self):
        sensorList = self.CallbackConnector.Scan_Callback()
        self.SensorListBox.clear()
        self.SensorListBox.addItems(sensorList)
        self.SensorListBox.setCurrentRow(0)

        if len(sensorList)>0:
            self.start_button.setEnabled(True)
        self.getpipelinestate()

    def start_callback(self):
        self.CallbackConnector.Start_Callback()
        self.stop_button.setEnabled(True)
        self.getpipelinestate()

    def stop_callback(self):
        self.CallbackConnector.Stop_Callback()
        self.reset_button.setEnabled(True)
        self.getpipelinestate()

    def reset_callback(self):
        self.CallbackConnector.Reset_Callback()
        self.getpipelinestate()
        self.reset_button.setEnabled(False)

    def home_callback(self):
        self.controller.showStartMenu()

    def sensorList_callback(self):
        curItem = self.SensorListBox.currentRow()
        modeList = self.CallbackConnector.getSampleModes(curItem)
        curModes = self.CallbackConnector.getCurMode()

        self.SensorModeList.clear()
        self.SensorModeList.addItems(modeList)
        self.SensorModeList.setCurrentText(curModes[0])

    def sensorModeList_callback(self):
        curItem = self.SensorListBox.currentRow()
        selMode = self.SensorModeList.currentText()
        if selMode != '':
            self.CallbackConnector.setSampleMode(curItem,selMode)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    CollectDataWindow = CollectDataWindow()
    CollectDataWindow.show()
    sys.exit(app.exec_())