using Aero.PipeLine;
using Basic_Streaming.NET.Views;
using DelsysAPI.Components.TrignoRf;
using DelsysAPI.DelsysDevices;
using DelsysAPI.Events;
using DelsysAPI.Exceptions;
using DelsysAPI.Pipelines;
using DelsysAPI.Utils;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;

namespace Basic_Streaming.NET
{
    /// <summary>
    /// Interaction logic for DeviceStreamUserControl.xaml
    /// </summary>
    public partial class DeviceStreaming : UserControl
    {
       
	// Add your API key & license here 

        private string key = "";
        private string license = "";


        public List<SensorTrignoRf> SelectedSensors;

        // Pipeline fields
        private IDelsysDevice _deviceSource;
        private Pipeline _pipeline;

        // Holds collection data
        private List<List<double>> _data;

        // Metadata fields
        private int _totalFrames;
        private int _totalLostPackets;
        private int _frameThroughput;
        private double _packetInterval;
        private double _streamTime = 0.0;

        // User Controls
        private StreamInfo _streamInfo;
        private PairSensor _pairSensor;
        private ScannedSensors _scannedSensors;

        MainWindow _mainWindow;

        public DeviceStreaming(MainWindow mainWindowPanel)
        {
            InitializeComponent();
            InitializeDataSource();
            _streamInfo = new StreamInfo();
            MainPanel.Children.Add(_streamInfo);
            _mainWindow = mainWindowPanel;
        }

        #region Device Configuration


        private void InitializeDataSource()
        {

            // The API uses a factory method to create the data source of your application.
            // This creates the factory method, which will then give the data source for your platform.
            // In this case, the platform is RF.
            var deviceSourceCreator = new DeviceSourcePortable(key, license);
            deviceSourceCreator.SetDebugOutputStream((str, args) => Trace.WriteLine(string.Format(str, args)));

            // Here is where we tell the factory method what type of data source we want to receive,
            // which we then set a reference to for future use.
            _deviceSource = deviceSourceCreator.GetDataSource(SourceType.TRIGNO_RF);

            // Here we use the key and license we previously loaded.
            _deviceSource.Key = key;
            _deviceSource.License = license;
        }

        private void LoadDataSource()
        {
            // Attempts to load device
            try
            {
                // Create a Pipeline based on the datasource.
                Debug.WriteLine("Creating pipeline...");
                PipelineController.Instance.AddPipeline(_deviceSource);
            }
            // Catches exception if no base is detected
            catch (BaseDetectionFailedException e)
            {
                return;
            }

            // Create a reference to this Pipeline
            _pipeline = PipelineController.Instance.PipelineIds[0];

            // Define the time (in seconds) we want to spend scanning for paired sensors.
            _pipeline.TrignoRfManager.InformationScanTime = 5;

            // Register handlers for API component (sensor specific) events
            _pipeline.TrignoRfManager.ComponentAdded += ComponentAdded;
            _pipeline.TrignoRfManager.ComponentLost += ComponentLost;
            _pipeline.TrignoRfManager.ComponentRemoved += ComponentRemoved;
            _pipeline.TrignoRfManager.ComponentScanComplete += ComponentScanComplete;

            // Register handlers for API collection events
            _pipeline.CollectionStarted += CollectionStarted;
            _pipeline.CollectionDataReady += CollectionDataReady;
            _pipeline.CollectionComplete += CollectionComplete;
        }

        public void ConfigurePipeline()
        {
            DataLine dataLine = new DataLine(_pipeline);
            dataLine.ConfigurePipeline();

            // Get the frame throughput (the number of Trigno frames passed from the API at a time)
            _frameThroughput = PipelineController.Instance.GetFrameThroughput();

            int totalChannels = 0;
            foreach (var comp in _pipeline.TrignoRfManager.Components)
            {
                totalChannels += comp.TrignoChannels.Count();
            }

            _streamInfo.Model.PipelineStatus = _pipeline.CurrentState.ToString();
            _streamInfo.PipelineStatus.Foreground = Brushes.Red;
            _streamInfo.Model.SensorsConnected = _pipeline.TrignoRfManager.Components.Count();
            _streamInfo.Model.TotalChannels = totalChannels;

            return;
        }

        public async Task StopStreamAsync()
        {
            await _pipeline.Stop();
        }

        public async Task ResetPipeline()
        {
            // Start reset by disarming pipeline
            await _pipeline.DisarmPipeline();

            _totalFrames = 0;
            _totalLostPackets = 0;
            _streamTime = 0.0;

            // Removes components from pipeline
            for (int i = 0; i < _pipeline.TrignoRfManager.Components.Count; i++)
            {
                Debug.WriteLine("Removing component...");
                _pipeline.TrignoRfManager.RemoveTrignoComponent(_pipeline.TrignoRfManager.Components[i]);
            }

        }

        #endregion

        #region API Component Event Handlers

        public void ComponentAdded(object sender, ComponentAddedEventArgs e)
        {
            Debug.WriteLine("ComponentAdded");
        }

        public void ComponentLost(object sender, ComponentLostEventArgs e)
        {
            Debug.WriteLine("ComponentLost");
        }

        public void ComponentRemoved(object sender, ComponentRemovedEventArgs e)
        {
            Debug.WriteLine("ComponentRemoved");
        }

        public void ComponentScanComplete(object sender, ComponentScanCompletedEventArgs e)
        {
            this.Dispatcher.Invoke(() => {
                _mainWindow.btn_backToMainPageButton.IsEnabled = true;
                btn_ScanSensors.IsEnabled = true;
                btn_Reset.IsEnabled = true;
                btn_PairSensors.IsEnabled = true;
            });
            // Check if no sensors were detected in scan
            if (e.ComponentDictionary.Count <= 0)
            {
                // Propmt user to try again if none found
                _scannedSensors.NoSensorsDetected();

                return;
            }

            Application.Current.Dispatcher.BeginInvoke(new Action(() =>
            {
                int sensorIndex = 0;
                foreach (var comp in _pipeline.TrignoRfManager.Components)
                {
                    comp.SelectSampleMode(comp.Configuration.SampleModes[0]);
                    sensorIndex++;
                }
            }));

            // Populated scanned sensors list.
            this.Dispatcher.Invoke(() => { _scannedSensors.ScanComplete(_pipeline.TrignoRfManager.Components); });
        }

        #endregion

        #region API Data Collection Event Handlers

        public void CollectionStarted(object sender, CollectionStartedEvent e)
        {
            this.Dispatcher.Invoke(() => {
                _mainWindow.btn_backToMainPageButton.IsEnabled = false;
                btn_Reset.IsEnabled = false;
                btn_Stop.IsEnabled = true;
            });

            _streamInfo.Model.PipelineStatus = _pipeline.CurrentState.ToString();

            _data = new List<List<double>>();
            _totalFrames = 0;
            _totalLostPackets = 0;

            int totalChannels = 0;

            // Recreate the list of data channels for recording.
            // First, iterate across all components
            for (int i = 0; i < _pipeline.TrignoRfManager.Components.Count; i++)
            {
                // then across all channels within each component.
                for (int j = 0; j < _pipeline.TrignoRfManager.Components[i].TrignoChannels.Count; j++)
                {
                    if (_data.Count <= totalChannels)
                    {
                        _data.Add(new List<double>());
                    }
                    else
                    {
                        _data[totalChannels] = new List<double>();
                    }
                    if (_packetInterval == 0)
                    {
                        _packetInterval = _pipeline.TrignoRfManager.Components[i].TrignoChannels[j].FrameInterval * _frameThroughput;
                    }
                    totalChannels++;
                }
            }

        }

        public void CollectionDataReady(object sender, ComponentDataReadyEventArgs e)
        {
            // Increment timer
            _streamTime += _packetInterval;

            int lostPackets = 0;

            // Checks to see if any of the packets were lost during the stream.
            // Loops through each frame data, since the API passes the data as n packets/frames, where n is the value of frameThroughput.
            // We need to check all frames to see if any data is lost from any of them.
            for (int k = 0; k < e.Data.Count(); k++)
            {
                // Loops through each sensor.
                for (int i = 0; i < e.Data[k].SensorData.Count(); i++)
                {
                    // Checks to see if any of the data in a sensor is lost.
                    if (e.Data[k].SensorData[i].IsDroppedPacket)
                    {
                        lostPackets++;
                    }
                }
            }
            _totalLostPackets += lostPackets;
            _totalFrames += _frameThroughput * e.Data[0].SensorData.Count();

            // Determines the column that the data will be inserted into.
            int columnIndex = 0;
            for (int k = 0; k < e.Data.Count(); k++)
            {
                // Loops through each connected sensors.
                for (int i = 0; i < e.Data[k].SensorData.Count(); i++)
                {
                    // Loops through each channel for each sensor.
                    for (int j = 0; j < e.Data[k].SensorData[i].ChannelData.Count(); j++)
                    {
                        // Loops through the data of each channel.
                        foreach (var val in e.Data[k].SensorData[i].ChannelData[j].Data)
                        {
                            // Adds the data at the current column index.
                            _data[columnIndex].Add(val);
                        }
                        columnIndex++;
                    }
                }
                // Resets column index so the next data in the second Trigno Frame gets added to the right channels.
                columnIndex = 0;
            }

            _streamInfo.Model.PacketsLost = _totalLostPackets;
            _streamInfo.Model.StreamTime = _streamTime.ToString("#.##") + " seconds";
            _streamInfo.Model.FramesCollected = _totalFrames;
        }

        public void CollectionComplete(object sender, CollectionCompleteEvent e)
        {
            this.Dispatcher.Invoke(() => {
                _mainWindow.btn_backToMainPageButton.IsEnabled = true;
                btn_Reset.IsEnabled = true;
                btn_Export.IsEnabled = true;
            });
        }

        #endregion

        #region Button Events Handlers

        public void clk_LoadDevice(object sender, RoutedEventArgs e)
        {
            InitializeDataSource();
            LoadDataSource();

            btn_LoadDevice.IsEnabled = false;
            btn_PairSensors.IsEnabled = true;
            btn_ScanSensors.IsEnabled = true;

            _streamInfo.Model.DeviceName = _deviceSource.PipelineIdentifier;
            _streamInfo.Model.PipelineStatus = _pipeline.CurrentState.ToString();
            _streamInfo.DeviceName.Foreground = Brushes.Green;
        }

        public async void clk_Scan(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("# of components before scan: " + _pipeline.TrignoRfManager.Components.Count);
            _mainWindow.btn_backToMainPageButton.IsEnabled = false;
            btn_Reset.IsEnabled = false;
            btn_ScanSensors.IsEnabled = false;
            btn_PairSensors.IsEnabled = false;

            // Remove any previously connected sensors from pipeline
            foreach (var comp in _pipeline.TrignoRfManager.Components)
            {
                await _pipeline.TrignoRfManager.DeselectComponentAsync(comp);
                _pipeline.TrignoRfManager.RemoveTrignoComponent(comp);
            }

            // Display scanned sensors user control.
            SecondaryPanel.Children.Clear();
            _scannedSensors = new ScannedSensors(this, _pipeline);
            SecondaryPanel.Children.Add(_scannedSensors);

            await _pipeline.Scan();
            System.Diagnostics.Debug.WriteLine("# of components after scan: " + _pipeline.TrignoRfManager.Components.Count);
        }

        public async void clk_Reset(object sender, RoutedEventArgs e)
        {
            // Reset stream info fields
            await ResetPipeline();
            resetUI();
            btn_PairSensors.IsEnabled = true;

        }

        public void resetUI()
        {
            _streamInfo.Model.PipelineStatus = _pipeline.CurrentState.ToString();
            _streamInfo.Model.StreamTime = "0.0 seconds";
            _streamInfo.Model.PacketsLost = 0;
            _streamInfo.Model.FramesCollected = 0;
            _streamInfo.PipelineStatus.Foreground = Brushes.Black;

            _totalFrames = 0;
            _totalLostPackets = 0;
            _streamTime = 0.0;

            btn_Stop.IsEnabled = false;
            btn_Reset.IsEnabled = false;
            btn_Export.IsEnabled = false;
            btn_Start.IsEnabled = false;
            
            btn_ScanSensors.IsEnabled = true;
            
        }

        public void clk_Pair(object sender, RoutedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("# of components before pair: " + _pipeline.TrignoRfManager.Components.Count);
            // Display pairing user control
            SecondaryPanel.Children.Clear();
            _pairSensor = new PairSensor(_pipeline, _mainWindow, this);
            SecondaryPanel.Children.Add(_pairSensor);

            btn_PairSensors.IsEnabled = false;
            btn_ScanSensors.IsEnabled = false;
        }

        public void clk_Export(object sender, RoutedEventArgs e)
        {
            List<string> lines = new List<string>();

            int nSensors = _pipeline.TrignoRfManager.Components.Count;
            int nChannels = _data.Count;

            string labelRow = "";

            foreach (var sensor in _pipeline.TrignoRfManager.Components.Where(x => x.State == SelectionState.Allocated))
            {

                foreach (var channel in sensor.TrignoChannels)
                {
                    System.Diagnostics.Debug.WriteLine("Channel Name: " + channel.Name);
                    labelRow += channel.Name + ",";
                }
            }

            int largestChannel = 0;
            for (int i = 1; i < nChannels; i++)
            {
                if (_data[i].Count > _data[largestChannel].Count)
                {
                    largestChannel = i;
                }
            }

            for (int i = 0; i < _data[largestChannel].Count; i++)
            {
                string dataRow = "";

                if (i == 0)
                {
                    dataRow += labelRow;
                    dataRow += "\n";
                }

                for (int j = 0; j < nChannels; j++)
                {
                    if (i < _data[j].Count) 
                    {
                        dataRow += _data[j].ElementAt(i).ToString() + ",";
                    }
                    else 
                    {
                        dataRow += ",";
                    }
                }

                lines.Add(dataRow);
            }

            string dataDir = "./sensor_data";
            if (!Directory.Exists(dataDir))
            {
                Directory.CreateDirectory(dataDir);
            }

            string fileName = DateTime.Now.ToString("yyy-dd-MM--HH-mm-ss");
            string path = dataDir + "/" + fileName + ".csv";
            using (StreamWriter outputFile = new StreamWriter(path))
            {
                foreach (string line in lines)
                {
                    outputFile.WriteLine(line);
                }
            }

            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo()
            {
                FileName = "sensor_data",
                UseShellExecute = true,
                Verb = "open"
            });


            btn_Export.IsEnabled = false;
        }

        public async void clk_Start(object sender, RoutedEventArgs e)
        {
            resetUI();

            await _pipeline.Start();

            btn_Start.IsEnabled = false;
            btn_ScanSensors.IsEnabled = false;
            _streamInfo.PipelineStatus.Foreground = Brushes.Green;
        }

        public async void clk_Stop(object sender, RoutedEventArgs e)
        {
            await StopStreamAsync();
            btn_Start.IsEnabled = true;
            btn_Stop.IsEnabled = false;
            //Pipeline transition from Finished to Armed - about 100ms to transistion to armed then pull current state
            Thread.Sleep(100);
            _streamInfo.Model.PipelineStatus = _pipeline.CurrentState.ToString();
            _streamInfo.PipelineStatus.Foreground = Brushes.Blue;
        }

        #endregion
    }
}
