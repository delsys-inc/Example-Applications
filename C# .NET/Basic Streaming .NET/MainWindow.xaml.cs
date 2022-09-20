using DelsysAPI.Pipelines;
using System.Windows;


namespace Basic_Streaming.NET
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private DeviceStreaming _deviceSteamingUC;

        public MainWindow()
        {
            InitializeComponent();
        }

        public void clk_DeviceStreaming(object sender, RoutedEventArgs e)
        {
            MainPanel.Children.Clear();
            _deviceSteamingUC = new DeviceStreaming(this);
            MainPanel.Children.Add(_deviceSteamingUC);
        }

        public void clk_Exit(object sender, RoutedEventArgs e)
        {
            System.Windows.Application.Current.Shutdown();
        }

        public void clk_BackButton(object sender, RoutedEventArgs e)
        {
            MainPanel.Children.Clear();

            MainPanel.Children.Add(MainWindowBorder);

            System.Diagnostics.Debug.WriteLine("Simulating Stream # of pipeline Ids before removal: " + PipelineController.Instance.PipelineIds.Count);
            if (PipelineController.Instance.PipelineIds.Count > 0)
            {
                PipelineController.Instance.RemovePipeline(0);
            }
            System.Diagnostics.Debug.WriteLine("Simulating Stream # of pipeline Ids after removal: " + PipelineController.Instance.PipelineIds.Count);
        }
    }
}
