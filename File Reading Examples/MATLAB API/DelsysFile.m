classdef DelsysFile < handle
    %Delsys File Wrapper for FileReaderAPI% 
    
    properties (Access = private)
       file;
    end
    
    methods  
        function obj = DelsysFile(delsysFile)
            obj.file = delsysFile;
        end
        
        function component = Component(obj, selectedComponent)
        %Component/Sensor Object - Pass component index and return the component object%
        
            tempComponent = obj.file.Components.Item(ShiftIndexing(obj, selectedComponent));
            component = Component(tempComponent);
        end
        
        function componentCount = ComponentCount(obj)
        %Returns the amount of sensor components in the file%
        
            componentCount = double(obj.file.Components.Count);
        end
        
        function data = GetAllData(obj)
        %Return all of the data from all sensor/component channels%
        
            componentCount = obj.ComponentCount();
            data = {};
            for i = 1:componentCount
                component = Component(i);
                componentData = component.GetAllData();
                for j = 1:length(componentData)
                    data{i} = componentData{j};
                end
            end
        end
    
    end
    
    methods(Access = private)
            
        % Shifts indexes left by 1 to adjust for the C# language that
        % starts indexing at 0 instead of 1 like matlab
        function shiftedIndex = ShiftIndexing(obj, index)
            shiftedIndex = index - 1;
        end
    end  
end

