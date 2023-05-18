"""
Controller class for the Data Collector GUI
This is the controller for the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

from collections import deque
import threading

from PySide2.QtWidgets import QMessageBox, QDialog

from Plotter.GenericPlot import *
from AeroPy.TrignoBase import *
from AeroPy.DataManager import *

clr.AddReference("System.Collections")

base = TrignoBase()
TrigBase = base.BaseInstance

app.use_app('PySide2')


class PlottingManagement:
    def __init__(self, metrics, emgplot=None):
        self.EMGplot = emgplot
        self.metrics = metrics
        self.packetCount = 0  # Number of packets received from base
        self.pauseFlag = True  # Flag to start/stop collection and plotting
        self.numSamples = 10000  # Default number of samples to visualize at a time
        self.DataHandler = DataKernel(TrigBase)  # Data handler for receiving data from base
        self.outData = [[0]]
        self.Index = None
        self.newTransform = None

    def streaming(self):
        """This is the data processing thread"""
        self.emg_queue = deque()
        while self.pauseFlag is True:
            continue
        while self.pauseFlag is False:
            self.DataHandler.processData(self.emg_plot)
            self.updatemetrics()

    def vispyPlot(self):
        """Plot Thread"""
        skipCount = 0
        while self.pauseFlag is False:
            if len(self.emg_plot) >= 2:
                incData = self.emg_plot.popleft()  # Data at time T-1
                self.outData = list(np.asarray(incData, dtype='object')[tuple([self.dataStreamIdx])])
                if self.dataStreamIdx and self.outData[0].size > 0:
                    try:
                        self.EMGplot.plot_new_data(self.outData, [self.emg_plot[0][i][0] for i in self.dataStreamIdx])
                    except IndexError:
                        print("Index Error Occurred: CollectDataController.py - line 49")

    def updatemetrics(self):
        self.metrics.framescollected.setText(str(self.DataHandler.packetCount))

    def threadManager(self, start_trigger, stop_trigger):
        """Handles the threads for the DataCollector gui"""
        self.emg_plot = deque()

        self.t1 = threading.Thread(target=self.streaming)
        self.t1.setDaemon(True)
        self.t1.start()

        if self.EMGplot:
            self.t2 = threading.Thread(target=self.vispyPlot)
            self.t2.setDaemon(True)
            if not start_trigger:
                self.t2.start()

        if start_trigger:
            self.t3 = threading.Thread(target=self.WaitingForStartTrigger)
            self.t3.start()

        if stop_trigger:
            self.t4 = threading.Thread(target=self.WaitingForStopTrigger)
            self.t4.start()

    def WaitingForStartTrigger(self):
        while TrigBase.IsWaitingForStartTrigger():
            continue
        self.pauseFlag = False
        if self.EMGplot:
            self.t2.start()
        print("Trigger Start - Collection Started")

    def WaitingForStopTrigger(self):
        while TrigBase.IsWaitingForStartTrigger():
            continue
        while TrigBase.IsWaitingForStopTrigger():
            continue
        self.pauseFlag = True
        self.metrics.pipelinestatelabel.setText(self.PipelineState_Callback())
        print("Trigger Stop - Data Collection Complete")
        self.DataHandler.processData(self.emg_plot)

    # ---------------------------------------------------------------------------------
    # ---- Callback Functions
    def PipelineState_Callback(self):
        return TrigBase.GetPipelineState()

    def Connect_Callback(self):
        """Callback to connect to the base"""
        TrigBase.ValidateBase(key, license)

    def FrameCount_Callback(self):
        return self.DataHandler.packetCount

    def Pair_Callback(self):
        """Callback to tell the base to enter pair mode for new sensors"""
        TrigBase.PairSensor()
        dialogbox = QDialog()
        dialogbox.setWindowTitle("Awaiting sensor pair request. . .")
        dialogbox.setFixedWidth(300)
        dialogbox.setFixedHeight(50)
        dialogbox.show()
        while TrigBase.CheckPairStatus():
            continue
        dialogbox.close()
        messagebox = QMessageBox()
        messagebox.setText("Pair another sensor?")
        messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        messagebox.setIcon(QMessageBox.Question)
        button = messagebox.exec_()

        if button == QMessageBox.Yes:
            self.Pair_Callback()
        else:
            self.Scan_Callback()

    def Scan_Callback(self):
        """Callback to tell the base to scan for any available sensors"""
        f = TrigBase.ScanSensors().Result
        self.nameList = TrigBase.GetSensorNames()
        self.SensorsFound = len(self.nameList)

        # TrigBase.SelectSensor(0)
        TrigBase.SelectAllSensors()
        return self.nameList

    def Start_Callback(self, start_trigger, stop_trigger):
        """Callback to start the data stream from Sensors"""
        if not start_trigger:
            self.pauseFlag = False
        self.metrics.framescollected.setText("0")
        self.DataHandler.packetCount = 0
        self.DataHandler.allcollectiondata = [[]]

        if TrigBase.GetPipelineState() == 'Armed':
            for i in range(len(self.channelnames)):
                self.DataHandler.allcollectiondata.append([])

        if TrigBase.GetPipelineState() == 'Connected':
            self.channelcount = 0
            TrigBase.Configure(start_trigger, stop_trigger)

            self.channelnames = []
            self.sampleRates = []
            self.samplesPerFrame = [[] for i in range(self.SensorsFound)]
            self.plotCount = 0
            # ---- Discover sensor channels
            self.dataStreamIdx = []  # This list indexes into the sensor data array, selecting relevant data to visualize
            idxVal = 0

            for i in range(self.SensorsFound):
                selectedSensor = TrigBase.GetSensorObject(i)
                if len(selectedSensor.TrignoChannels) > 0:
                    for channel in range(len(selectedSensor.TrignoChannels)):
                        self.channelcount += 1
                        self.DataHandler.allcollectiondata.append([])
                        self.channelnames.append(selectedSensor.TrignoChannels[channel].Name)
                        self.sampleRates.append(selectedSensor.TrignoChannels[channel].SampleRate)
                        self.samplesPerFrame.append(selectedSensor.TrignoChannels[channel].SamplesPerFrame)
                        # ---- Collect the EMG channels for visualization, excluding skin check channels
                        if "EMG" in selectedSensor.TrignoChannels[channel].Name:
                            if "TrignoAvanti" in str(selectedSensor) and "2" in selectedSensor.TrignoChannels[
                                channel].Name:  # Avanti skin check
                                pass
                            elif "AvantiDoubleMini" in str(selectedSensor) and "2" in selectedSensor.TrignoChannels[
                                channel].Name:  # Duo Mini skin check 1
                                pass
                            elif "AvantiDoubleMini" in str(selectedSensor) and "4" in selectedSensor.TrignoChannels[
                                channel].Name:  # Duo Mini skin check 2
                                pass
                            else:
                                self.dataStreamIdx.append(idxVal)
                                self.plotCount += 1
                        idxVal += 1
        self.metrics.totalchannels.setText(str(self.channelcount))
        if self.EMGplot:
            self.EMGplot.initiateCanvas(None, None, self.plotCount, 1, self.numSamples)
        TrigBase.Start()
        self.threadManager(start_trigger, stop_trigger)

    def Stop_Callback(self):
        """Callback to stop the data stream"""
        self.pauseFlag = True
        TrigBase.Stop()
        print("Data Collection Complete")

    # ---------------------------------------------------------------------------------
    # ---- Helper Functions
    def getSampleModes(self, sensorIdx):
        """Gets the list of sample modes available for selected sensor"""
        sampleModes = TrigBase.AvailibleSensorModes(sensorIdx)
        return sampleModes

    def getCurMode(self, sensorIdx):
        """Gets the current mode of the sensors"""
        curModes = TrigBase.GetCurrentSensorMode(sensorIdx)
        return curModes

    def setSampleMode(self, curSensor, setMode):
        """Sets the sample mode for the selected sensor"""
        TrigBase.SetSampleMode(curSensor, setMode)
