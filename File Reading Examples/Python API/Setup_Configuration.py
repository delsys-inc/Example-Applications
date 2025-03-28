def setup(path=None, debug=False):
    import os

    if debug:
        import platform
        print(platform.architecture())

    # For updating this code for newer builds, it's useful to have the directory point to the bin/build output
    outDirectory = path
    if outDirectory is None:
        #outDirectory = "...\ShpfWritingUtility\DelsysFileManager\bin\Release\net6.0"
        outDirectory = os.path.join(os.getcwd(), r"dependencies")
    
    pathToRuntimeConfigDll = os.path.join(outDirectory, r"Delsys.FileManager.runtimeconfig.json")

    from pythonnet import load
    load("coreclr", runtime_config=pathToRuntimeConfigDll)

    import pythonnet
    if debug: print(pythonnet.get_runtime_info())
    import clr
    import sys

    # Need to copy e_sqlite3.dll into the out directory from runtimes\win-x64\native tp
    sys.path.append(outDirectory)
    clr.AddReference("Delsys.FileManager")
   