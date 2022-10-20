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

```
pipx inject mpf ./

mpf_vpcom_bridge.exe
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
