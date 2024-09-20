from DataCollector.CollectDataWindow import CollectDataWindow
from StartMenu.StartWindow import StartWindow


class LandingScreenController():
    def __init__(self):
        self.startWindow = StartWindow(self)
        self.collectWindow = CollectDataWindow(self)

        self.startWindow.show()

        self.curHeight = 900
        self.curWidth = 1400

    def showStartMenu(self):
        self.collectWindow.close()
        self.startWindow.show()

    def showCollectData(self):
        self.startWindow.close()
        if self.startWindow.plot_enabled.isChecked():
            self.collectWindow.plot_enabled = True
            self.collectWindow.AddPlotPanel()
        self.collectWindow.SetCallbackConnector()
        self.collectWindow.connect_callback()
        self.collectWindow.show()
