Bridge Installation:

1. Register mpf-visual-pinball bridge (run cmd shell as Administrator):
python register_vpcom.py –register

2. Create Your MPF table folder. In Your config.yaml enter:
hardware:
    platform: virtual_pinball

3. In VPX edit script and replace the controller with:
```
Set Controller = CreateObject(“MPF.Controller”)
```

4. If your mpf instance is running on a different machine than the machine running Visual Pinball then tell the bridge where to connect using the Controller.Run() command parameters
- Default BCP server will listen on the loopbak/localhost interface so In order for this to work you need to tell your bcp server to listen on external network interface by altering your config.yaml file as following
```
bcp:
    servers:
        url_style:
            ip: 0.0.0.0
```
- Update your table script to specify the address and/or port of your server in the 
```
#Ex 1 : Different machine on port 5051
Controller.Run "mypinball"

#Ex 2 : Different machine and different port
Controller.Run "mypinball", 1337
```



Instructions for MPF installed via `pipx`:
The latest official installation instructions for MPF utilize `pipx` to create a virtual environment (venv) for MPF to run in. To install the mpf-visual-pinball bridge, it must be injected into the MPF venv.
1.  Open a command prompt and change directories (cd) to the folder containing the mpf_vpcom_bridge source code.

2. Run the following command to inject mpf_vpcom_bridge into the MPF venv.
```
pipx inject mpf ./
```
3. To register the bridge with Windows as a COM object, the following exe must be run as Administrator. 
```
mpf_vpcom_bridge.exe
```
NOTE: The exe may not be included in the PATH for Windows by default. It may be located in the Scripts folder of the MPF venv, for example: C:\Users\Me\.local\pipx\venvs\mpf\Scripts\mpf_vpcom_bridge.exe where Me is the Windows username for the session.

4. The bridge can be unregistered be passing the following argument to the exe as Administrator:
```
mpf_vpcom_bridge.exe --unregister
```

To run a game:

1. start MPF (mpf both), wait until the display has been initialized
2. start VPX (as Administrator).
3. Run VPX table.

Remarks:
The setting of cGamename in VPX is not used to establish or check the connection.
The VPX Bridge connects to the running MPF.

To run a test:

1. run "Start Test.cmd" or run shell command "python -m unittest"
