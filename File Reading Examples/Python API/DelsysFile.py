from uuid import UUID
from Component import Component

class DelsysFile:
    """Delsys .shpf File Wrapper for FileReaderAPI"""

    def __init__(self, file):
        self.file = file

    def Component(self, selectedComponent: int) -> Component:
        """Component/Sensor Object - Pass component index and return the component object"""

        tempComponent = self.file.Trial.Components[selectedComponent]
        return Component(tempComponent, self.file.Trial.DataStream)

    # This section is additional methods that do not exist in the base library
    def ComponentCount(self) -> int:
        """Returns the amount of sensor components in the file"""

        componentCount = len(self.file.Trial.Components)
        return componentCount

    def GetAllData(self):
        """Return all of the data from all sensor/component channels"""
        
        componentCount = self.ComponentCount()
        data = []
        for i in range(componentCount):
            component = Component(i)
            componentData = component.GetAllData()
            for x in componentData:
                data.append(x)
        return data

    def GetChannelTimeSeries(self, guid):
        return list(self.file.Trial.GetChannelXyData(guid).xData)

    def GetChannelXyData(self, guid):
        """Return xy data for a channel"""
        return self.file.Trial.GetChannelXyData(guid)

    def Name(self) -> str:
        """Return all of the data from all sensor/component channels"""
        return self.file.Trial.Name