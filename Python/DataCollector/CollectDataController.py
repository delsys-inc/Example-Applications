"""
Controller class for the Data Collector GUI
This is the controller for the GUI that lets you connect to a base, scan via rf for sensors, and stream data from them in real time.
"""

from collections import deque
import threading
from Plotter.GenericPlot import *
from AeroPy.TrignoBase import *
from AeroPy.DataManager import *

clr.AddReference("System.Collections")
from System.Collections.Generic import List
from System import Int32

import random

base = TrignoBase()
TrigBase = base.BaseInstance

app.use_app('PySide2')

class PlottingManagement():
    def __init__(self,EMGplot):
        self.EMGplot = EMGplot                      # Plot canvas for EMG data
        self.packetCount = 0                        # Number of packets received from base
        self.pauseFlag = False                      # Flag to start/stop collection and plotting
        self.numSamples = 10000                     # Default number of samples to visualize at a time
        self.DataHandler = DataKernel(TrigBase)     # Data handler for receiving data from base
        self.outData = [[0]]
        self.Index = None
        self.newTransform = None

    def streaming(self):
        """This is the data processing thread"""
        self.emg_queue = deque()
        while self.pauseFlag is False:
            self.DataHandler.processData(self.emg_plot)

    def vispyPlot(self):
        """Plot Thread"""
        skipCount = 0
        while self.pauseFlag is False:
            if len(self.emg_plot) >= 2:
                incData = self.emg_plot.popleft()       # Data at time T-1
                self.outData = list(np.asarray(incData, dtype='object')[tuple([self.dataStreamIdx])])
                if self.dataStreamIdx and self.outData[0].size > 0:
                    try:
                        self.EMGplot.plot_new_data(self.outData, [self.emg_plot[0][i][0] for i in self.dataStreamIdx])
                    except IndexError:
                        print("Index Error Occurred: CollectDataController.py - line 49")


    def threadManager(self):
        """Handles the threads for the DataCollector gui"""
        self.emg_plot = deque()

        t1 = threading.Thread(target=self.streaming)
        t2 = threading.Thread(target=self.vispyPlot)

        t1.setDaemon(True)
        t2.setDaemon(True)

        t1.start()
        t2.start()

    #---------------------------------------------------------------------------------
    #---- Callback Functions
    def PipelineState_Callback(self):
        return TrigBase.GetPipelineState()

    def Connect_Callback(self):
        """Callback to connect to the base"""
        TrigBase.ValidateBase(key, license)

    def Pair_Callback(self):
        """Callback to tell the base to enter pair mode for new sensors"""
        if TrigBase.GetPipelineState() == 'Finished' or TrigBase.GetPipelineState() == 'Armed':
            self.Reset_Callback()
        TrigBase.PairSensor()

    def Scan_Callback(self):
        """Callback to tell the base to scan for any available sensors"""
        if TrigBase.GetPipelineState() == 'Finished' or TrigBase.GetPipelineState() == 'Armed':
            self.Reset_Callback()

        f = TrigBase.ScanSensors().Result
        self.nameList = TrigBase.GetSensorNames()
        self.SensorsFound = len(self.nameList)

        #TrigBase.SelectSensor(0)
        TrigBase.SelectAllSensors()
        return self.nameList

    def Start_Callback(self):
        """Callback to start the data stream from Sensors"""
        self.pauseFlag = False
        if TrigBase.GetPipelineState() == 'Connected':

            TrigBase.Configure()
            self.sampleRates = [[] for i in range(self.SensorsFound)]
            self.samplesPerFrame = [[] for i in range(self.SensorsFound)]


            # ---- Discover sensor channels
            self.dataStreamIdx = []  # This list indexes into the sensor data array, selecting relevant data to visualize
            plotCount = 0
            idxVal = 0
            for i in range(self.SensorsFound):
                selectedSensor = TrigBase.GetSensorObject(i)
                if len(selectedSensor.TrignoChannels) > 0:
                    for channel in range(len(selectedSensor.TrignoChannels)):
                        self.sampleRates[i].append((selectedSensor.TrignoChannels[channel].SampleRate,
                                                    selectedSensor.TrignoChannels[channel].Name))
                        self.samplesPerFrame[i].append(selectedSensor.TrignoChannels[channel].SamplesPerFrame)
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
                                plotCount += 1
                        idxVal += 1

            # ---- Create the plotting canvas and begin visualization
            self.EMGplot.initiateCanvas(None, None, plotCount, 1, self.numSamples)

        TrigBase.Start()
        self.threadManager()

    def Stop_Callback(self):
        """Callback to stop the data stream"""
        TrigBase.Stop()
        self.pauseFlag = True
        print("Data Collection Complete")

    def Reset_Callback(self):
        TrigBase.ResetPipeline()

    #---------------------------------------------------------------------------------
    #---- Helper Functions
    def getSampleModes(self,sensorIdx):
        """Gets the list of sample modes available for selected sensor"""
        sampleModes = TrigBase.AvailibleSensorModes(sensorIdx)
        return sampleModes

    def getCurMode(self):
        """Gets the current mode of the sensors"""
        curModes = TrigBase.GetAllSampleModes()
        return curModes

    def setSampleMode(self,curSensor,setMode):
        """Sets the sample mode for the selected sensor"""
        TrigBase.SetSampleMode(curSensor,setMode)