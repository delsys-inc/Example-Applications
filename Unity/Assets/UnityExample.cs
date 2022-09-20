using DelsysAPI.Channels.Transform;
using DelsysAPI.Configurations;
using DelsysAPI.Configurations.DataSource;
using DelsysAPI.Contracts;
using DelsysAPI.DelsysDevices;
using DelsysAPI.Events;
using DelsysAPI.Pipelines;
using DelsysAPI.Transforms;
using DelsysAPI.Utils;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.Events;

public class UnityExample : MonoBehaviour
{
    //Paste key/license strings here
    private string key = "";
    private string license = "";


    /// <summary>
    /// Data structure for recording every channel of data.
    /// </summary>
    List<List<double>> Data = new List<List<double>>();
    public Button ScanButton;
    public Button StartButton;
    public Button StopButton;
    public Button SelectButton;
    public Button PairButton;
    IDelsysDevice DeviceSource = null;
    int TotalLostPackets = 0;
    int TotalDataPoints = 0;
    public Text APIStatusText, TestText, PipelineState;
    Pipeline RFPipeline;
    ITransformManager TransformManager;
    string text, pipeline_state;
    UnityEvent m_scan;
    bool select, scan, start, stop, pair;
    string[] compoentNames;
    List<List<List<double>>> AllCollectionData = new List<List<List<double>>>();
    VerticalLayoutGroup verticalLayoutGroup;

    // Use this for initialization
    void Start()
    {

        Debug.Log("Entered Start Function.");

        //Finding references to all the buttons in the scene
        ScanButton = GameObject.FindGameObjectWithTag ("ScanButton").GetComponent<Button>();
        ScanButton.onClick.AddListener((UnityEngine.Events.UnityAction) this.clk_Scan);
        
        StartButton = GameObject.FindGameObjectWithTag ("StartButton").GetComponent<Button>();
        StartButton.onClick.AddListener((UnityEngine.Events.UnityAction) this.clk_Start);

        StopButton = GameObject.FindGameObjectWithTag ("StopButton").GetComponent<Button>();
        StopButton.onClick.AddListener((UnityEngine.Events.UnityAction) this.clk_Stop);

        SelectButton = GameObject.FindGameObjectWithTag ("SelectButton").GetComponent<Button>();
        SelectButton.onClick.AddListener((UnityEngine.Events.UnityAction) this.clk_Select);

        PairButton = GameObject.FindGameObjectWithTag ("PairButton").GetComponent<Button>();
        PairButton.onClick.AddListener((UnityEngine.Events.UnityAction) this.clk_Pair);
        
        scan = true; //Enabling only the Scan button for now.
        start = false;
        stop = false;
        select = false;
        pair = false;

        CopyUSBDriver(); // Copying the SiUSBXp.dll file if not present
        InitializeDataSource(); //Initializing the Delsys API Data source
    }


    // Update is called once per frame
    void Update()
    {
        APIStatusText.text = text;
        SelectButton.enabled = select;
        ScanButton.enabled = scan;
        StartButton.enabled = start;
        StopButton.enabled = stop;
        PairButton.enabled = pair;
        PipelineState.text = PipelineController.Instance.PipelineIds[0].CurrentState.ToString();
    }

    public void CopyUSBDriver()
    {
        string unityAssetPath = Application.streamingAssetsPath + "/SiUSBXp.dll";
        string adjacentToExePath = Application.dataPath + "/../SiUSBXp.dll";
        if (!File.Exists(adjacentToExePath))
        {
            File.Copy(unityAssetPath, adjacentToExePath);
        }
    }

    /// <summary>
    /// Dumping all the debug statements from DelsysAPI into the Unity's Log file, see https://docs.unity3d.com/Manual/LogFiles.html for more details.
    /// </summary>
    /// <returns> None </returns>
    public void TraceWriteline(string s, object[] args)
    {
        for(int i=0; i< args.Count();i++){
            s = s + "; " + args[i];
        }
        Debug.Log("Delsys API:- " + s);
        
    }
   
    #region Initialization
    public void InitializeDataSource()
    {
        
        text = "Creating device source . . . ";
        if(key.Equals("") || license.Equals("")){
            text = "Please add your license details from the code.";
        }
        var deviceSourceCreator = new DeviceSourcePortable(key, license);
        deviceSourceCreator.SetDebugOutputStream(TraceWriteline);
        DeviceSource = deviceSourceCreator.GetDataSource(SourceType.TRIGNO_RF);
        text  = "Device source created.";
        DeviceSource.Key = key;
        DeviceSource.License = license;
        text = "Loading data source . . . ";

        try
        {
            LoadDataSource(DeviceSource);
        }
        catch(Exception exception)
        {
            text = "Something went wrong: " + exception.Message;
            return;
        }
        text = "Data source loaded and ready to Scan.";
    }

    public void LoadDataSource(IDelsysDevice ds)
    {
        PipelineController.Instance.AddPipeline(ds);

        RFPipeline = PipelineController.Instance.PipelineIds[0];
        TransformManager = PipelineController.Instance.PipelineIds[0].TransformManager;
        
        RFPipeline.TrignoRfManager.ComponentScanComplete += ComponentScanComplete;
        RFPipeline.CollectionStarted += CollectionStarted;
        RFPipeline.CollectionDataReady += CollectionDataReady;
        RFPipeline.CollectionComplete += CollectionComplete;
        RFPipeline.TrignoRfManager.ComponentAdded += ComponentAdded;
        RFPipeline.TrignoRfManager.ComponentLost += ComponentLost;
        RFPipeline.TrignoRfManager.ComponentRemoved += ComponentRemoved;        
    }

    #endregion

    #region Button Click events: clk_Scan, clk_Select, clk_Start, clk_Stop, clk_Pair
    public virtual async void clk_Scan()
    {
        Console.WriteLine("Scan Clicked");
        foreach(var comp in RFPipeline.TrignoRfManager.Components)
        {
            await RFPipeline.TrignoRfManager.DeselectComponentAsync(comp);
        }
        text = "Scanning . . .";
        await RFPipeline.Scan();
    }

    public virtual void clk_Select()
    {
        SelectSensors();
    }

    public virtual async void clk_Start()
    {
        
        // The pipeline must be reconfigured before it can be started again.      
        bool success = ConfigurePipeline();
        if(success){
            Debug.Log("Starting data streaming....");
            text = "Starting data streaming....";
            await RFPipeline.Start(); 
            stop = true; 
        }
        else{
            Debug.Log("Configuration failed. Cannot start streaming!!");  
            text = "Fatal error!";
        }
       
    }

    public virtual async void clk_Stop()
    {
        await RFPipeline.Stop();
    }

    public virtual async void clk_Pair()
    {
        text = "Awaiting a sensor pair . . .";
        await RFPipeline.TrignoRfManager.AddTrignoComponent(new System.Threading.CancellationToken());
    }

    #endregion

    public void SelectSensors()
    {
        text = "Selecting all sensors . . .";

        // Select every component we found and didn't filter out.
        foreach (var component in RFPipeline.TrignoRfManager.Components)
        {
            bool success = RFPipeline.TrignoRfManager.SelectComponentAsync(component).Result;
            if(success){
                text = component.FriendlyName + " selected!";
            }
            else{
                text = "Could not select sensor!!";
            }
        }       
        start = true;
    }


    /// <summary>
    /// Configures the input and output of the pipeline.
    /// </summary>
    /// <returns></returns>
    private bool ConfigurePipeline()
    {
        var inputConfiguration = new TrignoDsConfig();

        if (PortableIoc.Instance.CanResolve<TrignoDsConfig>())
        {
            PortableIoc.Instance.Unregister<TrignoDsConfig>();
        }

        PortableIoc.Instance.Register(ioc => inputConfiguration);

        foreach (var somecomp in RFPipeline.TrignoRfManager.Components.Where(x => x.State == SelectionState.Allocated))
        {       
            somecomp.SelectSampleMode(somecomp.DefaultMode);      
        }

        try
        {
            Debug.Log("Applying Input configurations");
            bool success_1 = RFPipeline.ApplyInputConfigurations(inputConfiguration);
            if(success_1){
                 text =  "Applied input configuration";
                 Debug.Log("Applied input configuration");
            }
            else{
                 text = "Input configurations failed";
                 Debug.Log("Input configurations failed");
            }
        }
        catch (Exception exception)
        {
            text = exception.Message;
        }
        RFPipeline.RunTime = int.MaxValue;

        TransformConnector transformConnector = new TransformConnector(RFPipeline);
        OutputConfig outputConfig = transformConnector.SetupTransforms();

        bool success_2 = RFPipeline.ApplyOutputConfigurations(outputConfig);
        if(success_2){
            text = "Applied Output configurations";
            Debug.Log("Applied Output configurations");
            return true;
        }
        else{
            text = "Output configurations failed!";
            Debug.Log("Output configurations failed!");
            return false;
        }        
    }
    


    #region Collection Callbacks -- Data Ready, Colleciton Started, and Collection Complete
    public virtual void CollectionDataReady(object sender, ComponentDataReadyEventArgs e)
    {
        //Channel based list of data for this frame interval
        List<List<double>> data = new List<List<double>>();

        for (int k = 0; k < e.Data.Count(); k++)
        {
            // Loops through each connected sensor
            for (int i = 0; i < e.Data[k].SensorData.Count(); i++)
            {
                // Loops through each channel for a sensor
                for (int j = 0; j < e.Data[k].SensorData[i].ChannelData.Count(); j++)
                {
                    data.Add(e.Data[k].SensorData[i].ChannelData[j].Data);
                }
            }

        }

        //Add frame data to entire collection data buffer
        AllCollectionData.Add(data);

        text = AllCollectionData.Count.ToString();
    }

    public virtual void CollectionStarted(object sender, DelsysAPI.Events.CollectionStartedEvent e)
    {
        AllCollectionData = new List<List<List<double>>>();
        text = "CollectionStarted event triggered!";
        var comps = PipelineController.Instance.PipelineIds[0].TrignoRfManager.Components;
        
        // Refresh the counters for display.
        TotalDataPoints = 0;
        TotalLostPackets = 0;

        // Recreate the list of data channels for recording
        int totalChannels = 0;
        for (int i = 0; i < comps.Count; i++)
        {
            for (int j = 0; j < comps[i].TrignoChannels.Count; j++)
            {
                if (Data.Count <= totalChannels)
                {
                    Data.Add(new List<double>());
                }
                else
                {
                    Data[totalChannels] = new List<double>();
                }
                totalChannels++;
            }
        }
    }

    public virtual async void CollectionComplete(object sender, DelsysAPI.Events.CollectionCompleteEvent e)
    {
        text = "CollectionComplete event triggered!";
        await RFPipeline.DisarmPipeline();
    }

    #endregion

    #region Component Events: Scan complete, Component Added, Lost, Removed
    public virtual void ComponentScanComplete(object sender, DelsysAPI.Events.ComponentScanCompletedEventArgs e)
    {
        text = "Scan Complete";

        select = true;
        pair = true;

    }

    public async void ComponentAdded(object sender, ComponentAddedEventArgs e)
    {

    }

    public virtual void ComponentLost(object sender, ComponentLostEventArgs e)
    {
        int sensorStickerNumber = RFPipeline.TrignoRfManager.Components.Where(sensor => sensor.Id == e.Component.Id).First().PairNumber;
        Console.WriteLine("It appears sensor " + sensorStickerNumber + " has lost connection. Please power cycle this sensor.");
        text = "It appears sensor " + sensorStickerNumber + " has lost connection";

    }

    public virtual void ComponentRemoved(object sender, ComponentRemovedEventArgs e)
    {

    }

    #endregion

}
