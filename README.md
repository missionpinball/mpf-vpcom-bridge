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

4. If your mpf instance is running on a different machine than the one running Visual Pinball then tell the bridge where to connect using the run command parameters
```
#Ex 1 : Different machine on port 5051
Controller.Run "mypinball"

#Ex 2 : Different machine and different port
Controller.Run "mypinball", 1337
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
