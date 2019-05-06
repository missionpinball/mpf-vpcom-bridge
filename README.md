Bridge Installation:
 
1. Register mpf-visual-pinball bridge (run cmd shell as Administrator):
python register_vpcom.py –register
 
2. Create Your MPF table folder. In Your config.yaml enter:
hardware:
    platform: virtual_pinball
 
3. In VPX edit script and replace the controller with:
Set Controller = CreateObject(“MPF.Controller”)
 
To run a game:
 
1. start MPF (mpf both), wait until the display has been initialized
2. start VPX (as Administrator).
3. Run VPX table.
 
Remarks:
The setting of cGamename in VPX is not used to establish or check the connection.
The VPX Bridge connects to the running MPF.