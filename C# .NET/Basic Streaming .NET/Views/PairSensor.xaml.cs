using DelsysAPI.Pipelines;
using System.Diagnostics;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using Microsoft.Toolkit.Uwp.Notifications;

namespace Basic_Streaming.NET.Views
{
    /// <summary>
    /// Interaction logic for PairSensor.xaml
    /// </summary>
    public partial class PairSensor : UserControl
    {
        private Pipeline _pipeline;

        private LoadingIcon _loadingIcon;

        private MainWindow _mainWindow;

        private DeviceStreaming _deviceStreaming;

        private System.Threading.CancellationTokenSource cancellationToken;

        private static readonly Regex _regex = new Regex("^[0-9]+$");
        private int[] IconMargin = { 97, -3, 108, 150 };
        private int[] msgMargin = { 0, 45, 0, 0 };
        private int[] msgONLYMargin = { 0, 22, 0, 0 };

        public PairSensor(Pipeline pipeline, MainWindow mainWindowPanel, DeviceStreaming deviceStreaming)
        {
            InitializeComponent();

            _pipeline = pipeline;

            _mainWindow = mainWindowPanel;

            _deviceStreaming = deviceStreaming;

            _deviceStreaming.btn_Reset.IsEnabled = true;

        }

        /// <summary>
        /// Asynchronously calls scanForPairRequest() as well as displaying messages according to the return bool value of scanForPairRequest().
        /// </summary>
        public async void selectComponentNumber()
        {
            // If the text only contains numbers.
            if(_regex.IsMatch(textbox_ForSensorNumber.Text))
            {
                // if the number entered exceeds the maximum number allowed (100,000).
                if(int.Parse(textbox_ForSensorNumber.Text) > 100000)
                {
                    UserInputLettersErrorMessage.Text = "The entered number is not within range (0-100,000)";
                    UserInputLettersErrorMessage.Visibility = Visibility;
                    return;
                }

                bool succeedInFindingAdditionalSensors = await ScanForPairRequestAsync(int.Parse(textbox_ForSensorNumber.Text));

                mainPageButtonAndResetButtonToggle(true);

                _deviceStreaming.btn_PairSensors.IsEnabled = true;

                _deviceStreaming.btn_ScanSensors.IsEnabled = true;

                // if the call to "ScanForPairRequestAsync" either exits because the number of components exceed supported
                //number of slots or it was unable to add/find additional sensors, then we will display a message telling them.
                if (!succeedInFindingAdditionalSensors)
                {
                    _loadingIcon.JustShowMessage("Could not find any additional sensors to pair...", msgONLYMargin);
                    return;
                }

                new ToastContentBuilder()
                .AddText($"Sensor {textbox_ForSensorNumber.Text} has been paired!")
                .Show();

                textbox_ForSensorNumber.Text = "";

                MainPanel.Children.Remove(_loadingIcon);

                TextBoxForSensorNumberDropDown.Visibility = Visibility.Visible;
                textbox_ForSensorNumber.Visibility = Visibility.Visible;
                textbox_ForSensorNumber.IsEnabled = true;
            }

            // If the user either does not enter anything or the user enters something that is not a number.
            else
            {
                UserInputLettersErrorMessage.Text = "Your input was not a valid integer. Please enter a valid integer.";
                UserInputLettersErrorMessage.Visibility = Visibility;
            }
        }

        /// <summary>
        /// Looks for any new sensors that have not been paired yet.
        /// </summary>
        /// <param name="sensorNumber"> Used to select the sensor number for the sensor (i.e. the default slot for the sensor).</param>
        /// <returns>False if there are no sensors to pair with. True if the program found a sensor to pair with.</returns>
        private async Task<bool> ScanForPairRequestAsync(int sensorNumber = 0)
        {
            TextBoxForSensorNumberDropDown.Visibility = Visibility.Collapsed;
            textbox_ForSensorNumber.Visibility = Visibility.Collapsed;
            textbox_ForSensorNumber.IsEnabled = false;

            mainPageButtonAndResetButtonToggle(false);

            _loadingIcon = new LoadingIcon("Scanning for pair requests...", IconMargin, msgMargin);
            MainPanel.Children.Add(_loadingIcon);

            cancellationToken = new System.Threading.CancellationTokenSource();

            // The number of components cannot exceed the number of available/supported slots.
            if (_pipeline.TrignoRfManager.Components.Count <= _pipeline.TrignoRfManager.SupportedNumberOfSlots())
            {
                return await _pipeline.TrignoRfManager.AddTrignoComponent(cancellationToken.Token, sensorNumber, false);
            }
            System.Diagnostics.Debug.WriteLine("# of components after pair: " + _pipeline.TrignoRfManager.Components.Count);

            // If it reaches this point, then the user has more activated sensors than supported slots.
            return false;
        }

        public void clk_AddSensor(object sender, RoutedEventArgs e)
        {

            UserInputLettersErrorMessage.Visibility = Visibility.Collapsed;
            selectComponentNumber();

        }

        private void mainPageButtonAndResetButtonToggle(bool shouldTurnOn)
        {
            _mainWindow.btn_backToMainPageButton.IsEnabled = shouldTurnOn;

            _deviceStreaming.btn_Reset.IsEnabled = shouldTurnOn;
        }

        private void clk_Cancel(object sender, RoutedEventArgs e)
        {
            cancellationToken.Cancel();
            (this.Parent as Grid).Children.Remove(this);

            mainPageButtonAndResetButtonToggle(true);

            _deviceStreaming.clk_Scan(new object(), new RoutedEventArgs());

            return;
        }
    }
}
