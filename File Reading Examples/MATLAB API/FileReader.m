classdef FileReader < handle
    %File Reader Interface to FileManagerAPI% 
    
    properties (Access = private)
       pathToDll;
       reader;
       file;
       trials;
       
    end
    
    methods  
        function obj = FileReader(pathToDll)
        %Pass path dll dependencies.% 
            dotnetenv("core");
            obj.pathToDll = pathToDll;
            NET.addAssembly(pathToDll + "Delsys.FileReader.dll");
            NET.addAssembly(pathToDll + "Delsys.FileManager.dll");
        end
        
        function Read(obj,filePath)
        %Pass path to .shpf file - FileReaderAPI will parse the file% 
            obj.reader = Delsys.FileManager.Reader.DelsysFileReader(filePath);
        end
        
        function file = ParsedFile(obj)
        %Once the file is paresd return the DelsysFile object% 
          obj.trials = obj.reader.OpenFileArray();
          file = DelsysFile(obj.trials(1));
        end

        function count = TrialCount(obj)
        %Number of trials in the file% 
          count = obj.trials.Length;
        end

        function file = Trial(obj, selectedTrial)
        %Get Trial at an index% 
          file = DelsysFile(obj.trials(selectedTrial));
        end
        
        function fileType = FileType(obj)
        %Returns the file type or extension% 
        
          fileType = string(obj.reader.FileType);
        end

        function Close(obj)
        %Closes the file type or extension% 
        
          obj.reader.Close();
        end
        
    end
    
end

