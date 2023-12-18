from PySide6.QtCore import Qt
from PySide6.QtWidgets import *


class CollectionMetricsManagement():
    def __init__(self):
        self.collectionmetrics = self.CollectionValuesPanel()


    def CollectionValuesPanel(self):
        collectionValuesPanel = QWidget()
        collectionvaluesLayout = QVBoxLayout()

        self.pipelinestatelabel = QLabel("-")
        self.pipelinestatelabel.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.pipelinestatelabel.setStyleSheet("color:white")
        collectionvaluesLayout.addWidget(self.pipelinestatelabel)

        self.sensorsconnected = QLabel('-')
        self.sensorsconnected.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.sensorsconnected.setStyleSheet("color : white ")
        collectionvaluesLayout.addWidget(self.sensorsconnected)

        self.totalchannels = QLabel('-')
        self.totalchannels.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.totalchannels.setStyleSheet("color : white ")
        collectionvaluesLayout.addWidget(self.totalchannels)

        self.framescollected = QLabel('-')
        self.framescollected.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.framescollected.setStyleSheet("color : white ")
        collectionvaluesLayout.addWidget(self.framescollected)
        collectionValuesPanel.setFixedWidth(200)
        collectionValuesPanel.setLayout(collectionvaluesLayout)

        return collectionValuesPanel