using DelsysAPI.Components.TrignoRf;
using DelsysAPI.Pipelines;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;

namespace Basic_Streaming.NET.Views
{
    /// <summary>
    /// Interaction logic for ScannedSensors.xaml
    /// </summary>
    public partial class ScannedSensors : UserControl
    {

        private Pipeline _pipeline;
        private List<SensorTrignoRf> _comps;
    
        private DeviceStreaming _uc;
        private LoadingIcon _loadingIcon;

        public ScannedSensors(DeviceStreaming uc, Pipeline pipeline)
        {
            InitializeComponent();
            _uc = uc;
            _pipeline = pipeline;
            _loadingIcon = new LoadingIcon("Scanning for paired sensors...");
            MainPanel.Children.Add(_loadingIcon);
        }

        public void ScanComplete(List<SensorTrignoRf> comps)
        {
            _comps = comps;
            MainPanel.Children.Remove(_loadingIcon);
            ScannedSensorsList.Visibility = Visibility.Visible;

            foreach (var sensor in comps)
            {
                SensorListItem item = new SensorListItem(sensor);
                ScannedSensorsList.Items.Add(item);
            }
        }

        public void NoSensorsDetected()
        {
            this.Dispatcher.Invoke(() =>
            {
                _loadingIcon.JustShowMessage("No sensors detected, please try again.");
                btn_ArmPipeline.Content = "Close";
            });
        }

        public void clk_ArmPipeline(object sender, RoutedEventArgs e)
        {
            if (btn_ArmPipeline.Content.ToString() == "Close")
            {
                (this.Parent as Grid).Children.Remove(this);
                return;
            }

            if (ScannedSensorsList.Items.Count == 0)
            {
                return;
            }

            int selectCount = 0;
            foreach(SensorListItem item in ScannedSensorsList.Items)
            {
                if (item.SelectCheckBox.IsChecked == true)
                {
                    foreach (var comp in _comps)
                    {
                        if (comp.Properties.Sid == item.Model.SensorId)
                        {
                            // Get index of selected mode in combobox
                            int modeIndex = item.ModeList.SelectedIndex;

                            // Use that index to set sensor mode
                            comp.SelectSampleMode(comp.Configuration.SampleModes[modeIndex]);

                            // Allocate sensor to pipeline
                            _pipeline.TrignoRfManager.SelectComponentAsync(comp).Wait();
                        }
                    }

                    selectCount++;
                }
            }

            // Return if no sensors in that list are detected
            if (selectCount <= 0)
            {
                return;
            }

            _uc.ConfigurePipeline();

            _uc.btn_PairSensors.IsEnabled = false;
            _uc.btn_ScanSensors.IsEnabled = false;
            _uc.btn_Start.IsEnabled = true;
            (this.Parent as Grid).Children.Remove(this);
        }

    }
}
