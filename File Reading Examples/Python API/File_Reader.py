from DelsysFile import DelsysFile
import clr

class File_Reader:
    """File Reader Interface to FileReaderAPI"""

    def __init__(self, dllPath):
        clr.AddReference(dllPath)
        self.filePath = ""
        self.reader = []

    def readFile(self, filePath):
        """Pass path to .shpf file - FileReaderAPI will parse the file"""
        import FileReader as FR
        self.filePath =  filePath
        self.reader = FR.ReadFile(filePath)

    def ParsedFile(self) -> DelsysFile:
        """Once the file is paresd return the DelsysFile object"""

        parsedFile = DelsysFile(self.reader.ParsedFile)
        return parsedFile

    def FileType(self) -> str:
        """Returns the file type or extension"""

        readType = int(self.reader.FileType)
        if readType == 1:
            fileType = '.shpf'
        else:
            fileType = 'Not a .shpf'
        return fileType