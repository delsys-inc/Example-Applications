from Component import Component

class DelsysFile:
    """Delsys .shpf File Wrapper for FileReaderAPI"""

    def __init__(self, file):
        self.file = file

    def Component(self, selectedComponent: int) -> Component:
        """Component/Sensor Object - Pass component index and return the component object"""

        tempComponent = self.file.Components[selectedComponent]
        return Component(tempComponent)

    # This section is additional methods that do not exist in the base library
    def ComponentCount(self) -> int:
        """Returns the amount of sensor components in the file"""

        componentCount = len(self.file.Components)
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