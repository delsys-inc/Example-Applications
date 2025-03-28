from DelsysFile import DelsysFile

class File_Reader:
    """File Reader Interface to FileReaderAPI"""

    def __init__(self):
        self.filePath = ""
        self.reader = []
        self.trials = []

    def readFile(self, filePath):
        """Pass path to .shpf file - FileReaderAPI will parse the file"""
        import Delsys.FileManager.Reader as FM
        self.filePath =  filePath
        self.reader = FM.DelsysFileReader(filePath)

    def ParsedFile(self) -> DelsysFile:
        """Once the file is parsed return the DelsysFile object"""
        self.trials = list(self.reader.OpenFileArray())
        return self.Trial(0)

    def Trial(self, selected_trial: int) -> DelsysFile:
        """Trial for given index"""
        return DelsysFile(self.trials[selected_trial])

    def TrialCount(self) -> int:
        """Returns the amount of trials in the file"""
        return len(self.trials)

    def Close(self):
        """Close the file"""
        self.reader.Close()

    def FileType(self) -> str:
        """Returns the file type or extension"""

        readType = int(self.reader.FileType)
        if readType == 1:
            fileType = '.shpf'
        elif readType == 5:
            fileType = '.delsys'
        else:
            fileType = 'Not a .shpf'
        return fileType