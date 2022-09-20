classdef FileReader < handle
    %File Reader Interface to FileReaderAPI% 
    
    properties (Access = private)
       pathToDll;
       reader;
       file;
       
    end
    
    methods  
        function obj = FileReader(pathToDll)
        %Pass path to FileReader.dll to initalize FileReader% 
        
            obj.pathToDll = pathToDll;
            NET.addAssembly(pathToDll);
        end
        
        function Read(obj,filePath)
        %Pass path to .shpf file - FileReaderAPI will parse the file% 
        
            obj.reader = FileReader.ReadFile(filePath);
        end
        
        function file = ParsedFile(obj)
        %Once the file is paresd return the DelsysFile object% 
        
          file = DelsysFile(obj.reader.ParsedFile);
        end
        
        function fileType = FileType(obj)
        %Returns the file type or extension% 
        
          fileType = string(obj.reader.FileType);
        end
        
    end
    
end

