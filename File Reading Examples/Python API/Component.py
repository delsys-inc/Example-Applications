from Channel import Channel

class Component:
    """Component class wrapper for FileReaderAPI"""

    def __init__(self, component):
        self.component = component

    def SensorId(self) -> int:
        """Component/Sensor ID - Unique ID of the sensor component"""

        sensorId = int(self.component.SensorId)
        return sensorId

    def Type(self) -> int:
        """Component Type - Number id associated with the sensor type"""
        type = int(self.component.Type)
        return type

    def ModeNumber(self) -> int:
        """Component Mode - Number id associated with the sensor mode"""

        modeNumber = int(self.component.ModeNumber)
        return modeNumber

    def SensorNumber(self) -> int:
        """Component/Sensor Pair Number - Assigned number for this sensor during a collection"""

        sensorNumber = int(self.component.SensorNumber)
        return sensorNumber

    def BatteryPercent(self) -> float:
        """Component/Sensor Battery Percent - Battery Percent at time of collection"""

        batteryPercent = float(self.component.BatteryPercent)
        return batteryPercent

    def PowerOnCount(self) -> int:
        """Component/Sensor Power On Count - Amount of times the sensor has been powered on"""

        powerOnCount = int(self.component.PowerOnCount)
        return powerOnCount

    def PowerOnTime(self) -> int:
        """Component/Sensor Power On Time - Amount of time the sensor has been on"""

        powerOnTime = int(self.component.PowerOnTime)
        return powerOnTime

    def Name(self) -> str:
        """Component/Sensor Name - This name can be set prior to a data stream"""

        name = str(self.component.Name)
        return name

    def FirmwareVersion(self) -> str:
        """Component/Sensor Firmware Version - A sensors firmware version at the time of collection"""

        firmwareVersion = str(self.component.FirmwareVersion)
        return firmwareVersion

    def Channel(self, selectedChannel: int) -> Channel:
        """Component/Sensor Channel Object - Pass channel index to return the channel object"""

        tempChannel = self.component.Channels[selectedChannel]
        channel = Channel(tempChannel)
        return channel

    def ChannelCount(self) -> int:
        """Component/Sensor Channel Count - Amount of channels collected by this sensor component"""
        
        channelCount = len(self.component.Channels)
        return channelCount

    # This section is additional methods that do not exist in the base library

    def GetAllData(self):
        """Return a list of all channel data from this sensor component"""

        channelCount = self.ChannelCount()
        data = []
        for i in range(channelCount):
            channel = self.Channel(i)
            data.append(channel.Data())
        return data

    def GetAllChannelNames(self) -> str:
        """Return a list of all channel names for this sensor component"""

        channelCount = self.ChannelCount()
        names = []
        for i in range(channelCount):
            channel = self.Channel(i)
            names.append(channel.Name())
        return names

    def GetAllSampleRates(self) -> str:
        """Return a list of all channel sample rates for this sensor component"""

        channelCount = self.ChannelCount()
        sampleRates = []
        for i in range(channelCount):
            channel = self.Channel(i)
            sampleRates.append(channel.SampleRate())
        return sampleRates
    
    def GetAllUnits(self) -> str:
        """Return a list of all channel units for this sensor component"""

        channelCount = self.ChannelCount()
        units = []
        for i in range(channelCount):
            channel = self.Channel(i)
            units.append(channel.Units())
        return units


