"""
This is the class that handles the data that is output from the Delsys Trigno Base.
Create an instance of this and pass it a reference to the Trigno base for initialization.
See CollectDataController.py for a usage example.
"""
import numpy as np


class DataKernel():
    def __init__(self, trigno_base):
        self.TrigBase = trigno_base
        self.packetCount = 0
        self.sampleCount = 0

    def processData(self, data_queue):
        """Processes the data from the Trigno Base and places it in the data_queue argument"""
        outArr = self.GetData()
        if outArr is not None:
            try:
                for i in range(len(outArr[0])):
                    if np.asarray(outArr[0]).ndim == 1:
                        data_queue.append(list(np.asarray(outArr, dtype='object')[0]))
                    else:
                        data_queue.append(list(np.asarray(outArr, dtype='object')[:, i]))
                try:
                    self.packetCount += len(outArr[0])
                    self.sampleCount += len(outArr[0][0])
                except:
                    pass
            except IndexError:
                pass

    def GetData(self):
        """Dictionary: Callback to get the data from the streaming sensors"""
        dataReady = self.TrigBase.CheckDataQueue()
        if dataReady:
            DataOut = self.TrigBase.PollData()
            outArr = [[] for i in range(len(DataOut.Keys))]
            keys = []
            for i in DataOut.Keys:
                keys.append(i)
            for j in range(len(DataOut.Keys)):
                outBuf = DataOut[keys[j]]
                outArr[j].append(np.asarray(outBuf, dtype='object'))
            return outArr
        else:
            return None


    # -----------------------------------------------------------
    # ---- Helper Functions
    def getPacketCount(self):
        return self.packetCount

    def resetPacketCount(self):
        self.packetCount = 0
        self.sampleCount = 0

    def getSampleCount(self):
        return self.sampleCount
