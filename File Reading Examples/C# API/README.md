# Delsys FileReader API - C# .NET Example

## Getting Started

Download this .NET example repository

Install Python [v3.8.10](https://www.python.org/downloads/release/python-3810/)

Install Jupyter Notebook - Open windows command prompt & run: 

`pip install notebook`

Install [.NET Core 6](https://dotnet.microsoft.com/en-us/download/dotnet/6.0)

Install dotnet interactive - Open windows command prompt & run:

`dotnet tool install --global Microsoft.dotnet-interactive --version 1.0.260601`

Add dontnet interactive to jupyter notebook by running:

`dotnet interactive jupyter install`

*If a file not found exception occurs on the FileReader.dll file, it may have been blocked by Windows during the unzip process. Go to file explorer, navigate to the python example directory, right click on FileReader.dll and choose properties, select Unblock and continue.

## Run in Jupyter Notebook

Open windows command prompt and navigate to local repository directory. Example: 

`cd ..\Example-Applications\File Reading Examples\C# API`

run: `jupyter notebook`

Jupyter notebook should open in your web browser. Open File_Reader_Example.ipynb file

Make sure ".NET (C#)" kernel is activated in the top right corner

Run individual code blocks or run the entire notebook. The code executed correctly if no errors occur, and plots are displayed in separate browser windows

## Run in Visual Studio Code

Download [VS Code](https://code.visualstudio.com/download)

Open VS Code and navigate to the FileReader_C#API directory

You may need to install the [Jupyter](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) and [.NET Interactive Notebook](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.dotnet-interactive-vscode) VS Code Extensions

Open File_Reader_Example.ipynb file and configure to the .NET Interactive kernel

Run individual code blocks or run the entire notebook. The code executed correctly if no errors occur, and plots are displayed in separate browser windows
