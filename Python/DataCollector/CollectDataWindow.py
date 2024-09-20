"""
Data Collector GUI
This is the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

import sys
import threading
import time
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from DataCollector.CollectDataController import *
import tkinter as tk
from tkinter import filedialog

from DataCollector.CollectionMetricsManagement import CollectionMetricsManagement
from Plotter import GenericPlot as gp


class CollectDataWindow(QWidget):
    plot_enabled = False

    def __init__(self, controller):
        QWidget.__init__(self)
        self.pipelinetext = "Off"
        self.controller = controller
        self.buttonPanel = self.ButtonPanel()
        self.plotPanel = None
        self.collectionLabelPanel = self.CollectionLabelPanel()

        self.grid = QGridLayout(self)

        self.MetricsConnector = CollectionMetricsManagement()
        self.collectionLabelPanel.setFixedHeight(275)
        self.MetricsConnector.collectionmetrics.setFixedHeight(275)

        self.metricspanel = QWidget()
        self.metricspane = QHBoxLayout()
        self.metricspane.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.metricspane.addWidget(self.collectionLabelPanel)
        self.metricspane.addWidget(self.MetricsConnector.collectionmetrics)
        self.metricspanel.setLayout(self.metricspane)
        self.metricspanel.setFixedWidth(400)
        self.grid.addWidget(self.buttonPanel, 0, 0)
        self.grid.addWidget(self.metricspanel, 0, 1)

        self.setStyleSheet("background-color:#3d4c51;")
        self.setLayout(self.grid)
        self.setWindowTitle("Collect Data GUI")
        self.pairing = False
        self.selectedSensor = None

    def AddPlotPanel(self):
        self.plotPanel = self.Plotter()
        self.grid.addWidget(self.plotPanel, 0, 2)

    def SetCallbackConnector(self):
        if self.plot_enabled:
            self.CallbackConnector = PlottingManagement(self, self.MetricsConnector, self.plotCanvas)
        else:
            self.CallbackConnector = PlottingManagement(self, self.MetricsConnector)

    # -----------------------------------------------------------------------
    # ---- GUI Components
    def ButtonPanel(self):
        buttonPanel = QWidget()
        buttonPanel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttonLayout = QVBoxLayout()
        findSensor_layout = QHBoxLayout()
        # ---- Pair Button
        self.pair_button = QPushButton('Pair', self)
        self.pair_button.setToolTip('Pair Sensors')
        self.pair_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.pair_button.objectName = 'Pair'
        self.pair_button.clicked.connect(self.pair_callback)
        self.pair_button.setStyleSheet('QPushButton {color: grey;}')
        self.pair_button.setEnabled(False)
        self.pair_button.setFixedHeight(50)
        findSensor_layout.addWidget(self.pair_button)

        # ---- Scan Button
        self.scan_button = QPushButton('Scan', self)
        self.scan_button.setToolTip('Scan for Sensors')
        self.scan_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.scan_button.objectName = 'Scan'
        self.scan_button.clicked.connect(self.scan_callback)
        self.scan_button.setStyleSheet('QPushButton {color: grey;}')
        self.scan_button.setEnabled(False)
        self.scan_button.setFixedHeight(50)
        findSensor_layout.addWidget(self.scan_button)

        buttonLayout.addLayout(findSensor_layout)

        triggerLayout = QHBoxLayout()

        self.starttriggerlabel = QLabel('Start Trigger', self)
        self.starttriggerlabel.setStyleSheet("color : grey")
        triggerLayout.addWidget(self.starttriggerlabel)
        self.starttriggercheckbox = QCheckBox()
        self.starttriggercheckbox.setEnabled(False)
        triggerLayout.addWidget(self.starttriggercheckbox)
        self.stoptriggerlabel = QLabel('Stop Trigger', self)
        self.stoptriggerlabel.setStyleSheet("color : grey")
        triggerLayout.addWidget(self.stoptriggerlabel)
        self.stoptriggercheckbox = QCheckBox()
        self.stoptriggercheckbox.setEnabled(False)
        triggerLayout.addWidget(self.stoptriggercheckbox)

        buttonLayout.addLayout(triggerLayout)

        # ---- Start Button
        self.start_button = QPushButton('Start', self)
        self.start_button.setToolTip('Start Sensor Stream')
        self.start_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.start_button.objectName = 'Start'
        self.start_button.clicked.connect(self.start_callback)
        self.start_button.setStyleSheet('QPushButton {color: grey;}')
        self.start_button.setEnabled(False)
        self.start_button.setFixedHeight(50)
        buttonLayout.addWidget(self.start_button)

        # ---- Stop Button
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setToolTip('Stop Sensor Stream')
        self.stop_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.stop_button.objectName = 'Stop'
        self.stop_button.clicked.connect(self.stop_callback)
        self.stop_button.setStyleSheet('QPushButton {color: grey;}')
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedHeight(50)
        buttonLayout.addWidget(self.stop_button)

        # ---- Export CSV Button
        self.exportcsv_button = QPushButton('Export CSV', self)
        self.exportcsv_button.setToolTip('Export collected data to project root - data.csv')
        self.exportcsv_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.exportcsv_button.objectName = 'Export'
        self.exportcsv_button.clicked.connect(self.exportcsv_callback)
        self.exportcsv_button.setStyleSheet('QPushButton {color: grey;}')
        self.exportcsv_button.setEnabled(False)
        self.exportcsv_button.setFixedHeight(50)
        buttonLayout.addWidget(self.exportcsv_button)

        # ---- Drop-down menu of sensor modes
        self.SensorModeList = QComboBox(self)
        self.SensorModeList.setToolTip('Sensor Modes')
        self.SensorModeList.objectName = 'PlaceHolder'
        self.SensorModeList.setStyleSheet('QComboBox {color: white;background: #848482}')
        buttonLayout.addWidget(self.SensorModeList)

        # ---- List of detected sensors
        self.SensorListBox = QListWidget(self)
        self.SensorListBox.setToolTip('Sensor List')
        self.SensorListBox.objectName = 'PlaceHolder'
        self.SensorListBox.setStyleSheet('QListWidget {color: white;background:#848482}')
        self.SensorListBox.itemClicked.connect(self.sensorList_callback)
        self.SensorListBox.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        buttonLayout.addWidget(self.SensorListBox)
        buttonPanel.setLayout(buttonLayout)
        buttonPanel.setFixedWidth(275)
        return buttonPanel

    def Plotter(self):
        widget = QWidget()
        widget.setLayout(QVBoxLayout())

        plot_mode = 'windowed'  # Select between 'scrolling' and 'windowed'
        pc = gp.GenericPlot(plot_mode)
        pc.native.objectName = 'vispyCanvas'
        pc.native.parent = self
        label = QLabel("*This Demo plots EMG Channels only")
        label.setStyleSheet('.QLabel { font-size: 8pt;}')
        label.setFixedHeight(20)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        widget.layout().addWidget(pc.native)
        widget.layout().addWidget(label)
        self.plotCanvas = pc

        return widget

    def CollectionLabelPanel(self):
        collectionLabelPanel = QWidget()
        collectionlabelsLayout = QVBoxLayout()

        pipelinelabel = QLabel('Pipeline State:')
        pipelinelabel.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        pipelinelabel.setStyleSheet("color:white")
        collectionlabelsLayout.addWidget(pipelinelabel)

        sensorsconnectedlabel = QLabel('Sensors Connected:', self)
        sensorsconnectedlabel.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        sensorsconnectedlabel.setStyleSheet("color:white")
        collectionlabelsLayout.addWidget(sensorsconnectedlabel)

        totalchannelslabel = QLabel('Total Channels:', self)
        totalchannelslabel.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        totalchannelslabel.setStyleSheet("color:white")
        collectionlabelsLayout.addWidget(totalchannelslabel)

        framescollectedlabel = QLabel('Frames Collected:', self)
        framescollectedlabel.setAlignment(Qt.AlignCenter | Qt.AlignRight)
        framescollectedlabel.setStyleSheet("color:white")
        collectionlabelsLayout.addWidget(framescollectedlabel)

        collectionLabelPanel.setFixedWidth(200)
        collectionLabelPanel.setLayout(collectionlabelsLayout)

        return collectionLabelPanel

    # -----------------------------------------------------------------------
    # ---- Callback Functions
    def getpipelinestate(self):
        self.pipelinetext = self.CallbackConnector.base.PipelineState_Callback()
        self.MetricsConnector.pipelinestatelabel.setText(self.pipelinetext)

    def connect_callback(self):
        self.CallbackConnector.base.Connect_Callback()

        self.pair_button.setEnabled(True)
        self.pair_button.setStyleSheet('QPushButton {color: white;}')
        self.scan_button.setEnabled(True)
        self.scan_button.setStyleSheet('QPushButton {color: white;}')
        self.starttriggerlabel.setStyleSheet("color : white")
        self.stoptriggerlabel.setStyleSheet("color : white")
        self.starttriggercheckbox.setEnabled(True)
        self.stoptriggercheckbox.setEnabled(True)
        self.getpipelinestate()
        self.MetricsConnector.pipelinestatelabel.setText(self.pipelinetext + " (Base Connected)")

    def pair_callback(self):
        """Pair button callback"""
        self.Pair_Window()
        self.getpipelinestate()
        self.exportcsv_button.setEnabled(False)
        self.exportcsv_button.setStyleSheet("color : gray")

    def Pair_Window(self):
        """Open pair sensor window to set pair number and begin pairing process"""
        pair_number, pressed = QInputDialog.getInt(QWidget(), "Input Pair Number", "Pair Number:",
                                                   1, 0, 100, 1)
        if pressed:
            self.pairing = True
            self.pair_canceled = False
            self.CallbackConnector.base.pair_number = pair_number
            self.PairThreadManager()

    def PairThreadManager(self):
        """Start t1 thread to begin pairing operation in DelsysAPI
           Start t2 thread to await result of CheckPairStatus() to return False
           Once threads begin, display awaiting sensor pair request window/countdown"""

        self.t1 = threading.Thread(target=self.CallbackConnector.base.Pair_Callback)
        self.t1.start()

        self.t2 = threading.Thread(target=self.awaitPairThread)
        self.t2.start()

        self.BeginPairingUISequence()


    def BeginPairingUISequence(self):
        """The awaiting sensor window will stay open until either:
           A) The pairing countdown timer completes (The end of the countdown will send a CancelPair request to the DelsysAPI)
           or...
           B) A sensor has been paired to the base (via self.pairing flag set by DelsysAPI CheckPairStatus() bool)

           If a sensor is paired, ask the user if they want to pair another sensor (No = start a scan for all previously paired sensors)
        """

        pair_success = False
        self.pair_countdown_seconds = 15

        awaitingPairWindow = QDialog()
        awaitingPairWindow.setWindowTitle(
            "Sensor (" + str(self.CallbackConnector.base.pair_number) + ") Awaiting sensor pair request. . . Cancel in: " + str(self.pair_countdown_seconds))
        awaitingPairWindow.setFixedWidth(500)
        awaitingPairWindow.setFixedHeight(80)
        awaitingPairWindow.show()

        while self.pair_countdown_seconds > 0:
            if self.pairing:
                time.sleep(1)
                self.pair_countdown_seconds -= 1
                self.UpdateTimerUI(awaitingPairWindow)
            else:
                pair_success = True
                break

        awaitingPairWindow.close()
        if not pair_success:
            self.CallbackConnector.base.TrigBase.CancelPair()
        else:
            self.ShowPairAnotherSensorDialog()

    def awaitPairThread(self):
        """ Wait for a sensor to be paired
        Once PairSensor() command is sent to the DelsysAPI, CheckPairStatus() will return True until a sensor has been paired to the base"""
        time.sleep(1)
        while self.pairing:
            pairstatus = self.CallbackConnector.base.CheckPairStatus()
            if not pairstatus:
                self.pairing = False

    def UpdateTimerUI(self, awaitingPairWindow):
        awaitingPairWindow.setWindowTitle(
            "Sensor (" + str(self.CallbackConnector.base.pair_number) + ") Awaiting sensor pair request. . . Cancel in: " + str(self.pair_countdown_seconds))

    def ShowPairAnotherSensorDialog(self):
        messagebox = QMessageBox()
        messagebox.setText("Pair another sensor?")
        messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        messagebox.setIcon(QMessageBox.Question)
        button = messagebox.exec_()

        if button == QMessageBox.Yes:
            self.Pair_Window()
        else:
            self.scan_callback()

    def scan_callback(self):
        sensorList = self.CallbackConnector.base.Scan_Callback()

        self.set_sensor_list_box(sensorList)

        if len(sensorList) > 0:
            self.start_button.setEnabled(True)
            self.start_button.setStyleSheet("color : white")
            self.stop_button.setEnabled(True)
            self.stop_button.setStyleSheet("color : white")
            self.MetricsConnector.sensorsconnected.setText(str(len(sensorList)))
            self.starttriggercheckbox.setEnabled(True)
            self.stoptriggercheckbox.setEnabled(True)
        self.getpipelinestate()
        self.exportcsv_button.setEnabled(False)
        self.exportcsv_button.setStyleSheet("color : gray")

    def set_sensor_list_box(self, sensorList):
        self.SensorListBox.clear()

        number_and_names_str = []
        for i in range(len(sensorList)):
            number_and_names_str.append("(" + str(sensorList[i].PairNumber) + ") " + sensorList[i].FriendlyName)
            for j in range(len(sensorList[i].TrignoChannels)):
                if sensorList[i].TrignoChannels[j].IsEnabled and not str(sensorList[i].TrignoChannels[j].Type) == "SkinCheck":
                    number_and_names_str[i] += "\n     -" + sensorList[i].TrignoChannels[j].Name + " (" + str(
                        round(sensorList[i].TrignoChannels[j].SampleRate, 3)) + " Hz)"

        self.SensorListBox.addItems(number_and_names_str)

    def start_callback(self):
        self.CallbackConnector.base.Start_Callback(self.starttriggercheckbox.isChecked(),
                                                   self.stoptriggercheckbox.isChecked())
        self.CallbackConnector.resetmetrics()
        self.starttriggercheckbox.setEnabled(False)
        self.stoptriggercheckbox.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.exportcsv_button.setEnabled(False)
        self.exportcsv_button.setStyleSheet("color : gray")
        self.getpipelinestate()

    def stop_callback(self):
        self.CallbackConnector.base.Stop_Callback()
        self.getpipelinestate()
        self.exportcsv_button.setEnabled(True)
        self.exportcsv_button.setStyleSheet("color : white")

    def exportcsv_callback(self):
        export = None
        if self.CallbackConnector.streamYTData:
            export = self.CallbackConnector.base.csv_writer.exportYTCSV()
        else:
            export = self.CallbackConnector.base.csv_writer.exportCSV()
        self.getpipelinestate()
        print("CSV Export: " + str(export))

    def sensorList_callback(self):
        current_selected = self.SensorListBox.currentRow()
        if self.selectedSensor is None or self.selectedSensor != current_selected:
            if self.selectedSensor is not None:
                self.SensorModeList.currentIndexChanged.disconnect(self.sensorModeList_callback)
            self.selectedSensor = self.SensorListBox.currentRow()
            modeList = self.CallbackConnector.base.getSampleModes(self.selectedSensor)
            curMode = self.CallbackConnector.base.getCurMode(self.selectedSensor)

            if curMode is not None:
                self.resetModeList(modeList)
                self.SensorModeList.setCurrentText(curMode)
                self.starttriggercheckbox.setEnabled(True)
                self.stoptriggercheckbox.setEnabled(True)
                self.SensorModeList.currentIndexChanged.connect(self.sensorModeList_callback)

    def resetModeList(self, mode_list):
        self.SensorModeList.clear()
        self.SensorModeList.addItems(mode_list)

    def sensorModeList_callback(self):
        curItem = self.SensorListBox.currentRow()
        curMode = self.CallbackConnector.base.getCurMode(curItem)
        selMode = self.SensorModeList.currentText()
        if curMode != selMode:
            if selMode != '':
                self.CallbackConnector.base.setSampleMode(curItem, selMode)
                self.getpipelinestate()
                self.starttriggercheckbox.setEnabled(True)
                self.stoptriggercheckbox.setEnabled(True)

                sensorList = self.CallbackConnector.base.TrigBase.GetScannedSensorsFound()
                self.set_sensor_list_box(sensorList)
                self.SensorModeList.setCurrentText(selMode)
                self.SensorListBox.setCurrentRow(curItem)
