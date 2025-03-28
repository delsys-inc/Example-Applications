from enum import Enum
from uuid import UUID
import numpy as np

class Channel:
    """Channel class wrapper for FileReaderAPI"""

    def __init__(self, channel, data):
        self.channel = channel
        self.data = data

    def Name(self) -> str:
        """Channel Name - This name can be set prior to a data stream"""

        name = str(self.channel.Name)
        return name

    def SampleRate(self) -> float:
        """Channel Sample Rate - The amount data points per second this channel was collected at"""

        sampleRate = float(self.channel.SampleRate)
        return sampleRate

    def Units(self) -> str:
        """Channel Unit - The unit of measurement for this channel"""

        units = str(Units(int(self.channel.Units)).name)
        return units

    def RangeMin(self) -> float:
        """Channel Minimum Range - The minimum value a data point can be"""

        rangeMin = float(self.channel.RangeMin)
        return rangeMin

    def RangeMax(self) -> float:
        """Channel Maximum Range - The maximum value a data point can be"""

        rangeMax = float(self.channel.RangeMax)
        return rangeMax

    def LogThisChannel(self) -> bool:
        """Channel Logging - Was this channel displayed during data collection"""

        logThisChannel = bool(self.channel.LogThisChannel)
        return logThisChannel

    def InternalName(self) -> str:
        """Channel Logging - Was this channel displayed during data collection"""

        internalName = str(self.channel.InternalName)
        return internalName

    def ChannelType(self) -> str:
        """Channel Type - Type of channel (ie. EMG, ACC, GYRO)"""

        type = str(self.channel.ChannelType)
        return type

    def SamplesPerFrame(self) -> int:
        """Channel Width - Amount of data points received on this channel per frame"""

        channelWidth = int(self.channel.SamplesPerFrame)
        return channelWidth


    def LocalChannelNumber(self):
        """Channel Local Index - Channel index based on all the sensor component channels"""

        localChannelNumber = int(self.channel.LocalChannelNumber)
        return localChannelNumber

    def Guid(self) -> str:
        return self.channel.GuidString;

    def Data(self):
        """Channel Data - All of the data associated with this channel during the collection"""
        return list(self.channel.GetYData(self.data))

class Units(Enum):
        Unknown = 0
        VOLTS = 1
        MILLIVOLTS = 2
        G = 3
        MICROTESLA = 4
        DEG_S = 5
        DEGS = 6
        Quaternion = 7
        QuaternionAccuracy = 8
        Orientation = 9
        OrientationAccuracy = 10
        Hz = 11
        Percentage = 12
        N_4cm2 = 13
        N = 14
        Revolutions = 15
        g_dl = 16
        BPM = 17
        METERS_SECOND = 18
        METERS = 19
        RPM = 20
        RADIANS_S = 21
        Nm = 22
        WATTS = 23
        Amplitude = 24
        Kilograms = 25
        Cycle = 26
        L = 27
        L_min = 28
        mL_kg_min = 29
        BrPM = 30,
        mL_min = 31