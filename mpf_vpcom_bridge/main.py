"""Brige between virtual pinball and MPF.

Based on proc-visual-pinball of destruk, Gerry Stellenberg, Adam Preble and Michael Ocean.
"""
import asyncio
import sys
import logging


try:
    import win32com
    import win32com.server.util
    from win32com.server.util import wrap, unwrap
    import pythoncom
    from win32com.server.exception import COMException
    import winerror
except ImportError:
    win32com = None
    util = None
    wrap = None
    unwrap = None
    pythoncom = None
    COMException = AssertionError
    winerror = None

from mpf.core.bcp.bcp_socket_client import AsyncioBcpClientSocket

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    filename="mpf-vpcom-bridge.txt")


class ISettings:
    _public_methods_ = []
    _public_attrs_ = [  'Value']

    def Value(self, item, item2):
        del item
        del item2
        return True

    def SetValue(self, item, item2):
        del item
        del item2
        return True


class IGames:
    _public_methods_ = []
    _public_attrs_ = [  'Settings']

    def Settings(self):
        settings = ISettings()
        Settings = wrap( settings )
        return Settings

    def SetSettings(self):
        settings = ISettings()
        Settings = wrap( settings )
        return Settings


class Controller:

    """Main Visual Pinball COM interface class."""

    _public_methods_ = [
        'Run',
        'Stop',
        'PrintGlobal',
        'PulseSW',
        'IsCoilActive'
    ]
    _reg_progid_ = "MPF.Controller"                         # Visual MPF Controller
    _reg_clsid_ = "{196FF002-17F9-4714-4242-A7BD39AD413B}"  # use a unique class guid for Visual MPF Controller
    _public_attrs_ = [
        'Version',
        'GameName',
        'Games',
        'SplashInfoLine',
        'ShowTitle',
        'ShowFrame',
        'ShowDMDOnly',
        'HandleMechanics',
        'HandleKeyboard',
        'DIP',
        'Switch',
        'Mech',
        'Pause',
        'ChangedSolenoids',
        'ChangedGIStrings',
        'ChangedLamps',
        'ChangedLEDs',
        'ChangedBrightnessLEDs',
        'ChangedFlashers',
        'HardwareRules',
        'GetMech'
    ]

    _readonly_attrs_ = [
        'Version',
        'ChangedSolenoids',
        'ChangedLamps',
        'ChangedGIStrings',
        'ChangedLEDs',
        'ChangedBrightnessLEDs',
        'ChangedFlashers',
        'HardwareRules',
        'GetMech'
    ]

    Version = "22222222"
    ShowTitle = None
    ShowFrame = False
    ShowDMDOnly = False
    HandleKeyboard = False
    DIP = False
    GameName = "Game name"

    Pause = None

    HandleMechanics = True
    ErrorMsg = "Python Failed -- check the log"

    def __init__(self, *, loop=None):
        self._reg_clsctx_ = pythoncom.CLSCTX_LOCAL_SERVER   # LocalSever (no InProc) only means game reloads entirely
        self.bcp_client = None
        self.last_switch = None
        self.switches = {}
        if not loop:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop

    # Need to overload this method to tell that we support IID_IServerWithEvents
    def _query_interface_(self, iid):
        """ Return this main interface if the IController class is queried. """
        IID_IController = pythoncom.MakeIID('{CE9ECC7C-960F-407E-B27B-62E39AB1E30F}')
        if iid == IID_IController:
            return win32com.server.util.wrap(self)

    def PrintGlobal(self):
        """Unused."""
        logging.getLogger('vpcom').info("PrintGlobal called.")
        return True

    def _connect(self, addr, port):
        """Connect to MPF."""
        try:
            reader, writer = self.loop.run_until_complete(asyncio.open_connection(addr, port))
            self.bcp_client = AsyncioBcpClientSocket(writer, reader)
        except Exception as e:
            raise COMException(desc="Failed to connect to MPF: {}".format(e), scode=winerror.E_FAIL)

    def Run(self, addr="localhost", port=5051):
        """Connect to MPF."""
        logging.getLogger('vpcom').info("Starting bridge. Connecting to {}:{}".format(addr,port))

        self._connect(addr, port)

        self.bcp_client.send("vpcom_bridge", {"subcommand": "start"})
        self.loop.run_until_complete(self.bcp_client.wait_for_response("vpcom_bridge_response"))

        return True

    def Stop(self):
        if self.bcp_client:
            self.bcp_client.send("vpcom_bridge", {"subcommand": "stop"})
            self.loop.run_until_complete(self.bcp_client.wait_for_response("vpcom_bridge_response"))
            self.bcp_client = None

        sys.exit(1)

    def Games(self, rom_name):
        """Return the IGames interface, by wrapping the object."""
        del rom_name
        games = IGames()
        wrapped_games = wrap (games)
        return wrapped_games

    def SetGames(self, rom_name):
        """Return the IGames interface, by wrapping the object."""
        del rom_name
        games = IGames()
        wrapped_games = wrap (games)
        return wrapped_games

    def _raise_error(self, desc):
        raise COMException(desc=desc, scode=winerror.E_FAIL)

    def _dispatch_to_mpf(self, command, **params):
        """Dispatch to MPF and wait for result."""
        params["subcommand"] = command
        try:
            self.bcp_client.send("vpcom_bridge", params)
            response = self.loop.run_until_complete(self.bcp_client.wait_for_response("vpcom_bridge_response"))
            response_data = response[1]
            if "error" in response_data:
                self._raise_error(desc="MPF reported an error as response to command {} ({}): {}".format(
                    command, params, response_data["error"]))
            if "result" not in response_data:
                self._raise_error(desc="MPF did not return a result {} ({}): {}".format(
                    command, params, response_data))
            return response_data["result"]
        except Exception as e:
            self._raise_error(desc="Failed to communicate with MPF at command {} ({}): {}".format(
                command, params, e))

    def Switch(self, number):
        """Return the current value of the requested switch."""
        return self._dispatch_to_mpf("switch", number=number)

    def GetSwitch(self, number):
        """Return the current value of the requested switch."""
        return self._dispatch_to_mpf("get_switch", number=number)

    def SetSwitch(self, number, value):
        """Set the value of the requested switch."""
        return self._dispatch_to_mpf("set_switch", number=number, value=value)

    def PulseSW(self, number):
        """Pulse Switch."""
        return self._dispatch_to_mpf("pulsesw", number=number)

    def Mech(self, number):
        """Currently unused."""
        return self._dispatch_to_mpf("mech", number=number)

    def SetMech(self, number, value):
        """Currently unused."""
        return self._dispatch_to_mpf("set_mech", number=number, value=value)

    def GetMech(self, number):
        """Currently unused."""
        return self._dispatch_to_mpf("get_mech", number=number)

    def ChangedSolenoids(self):
        """Return a list of changed coils."""
        return self._dispatch_to_mpf("changed_solenoids")

    def ChangedLamps(self):
        """Return a list of changed lamps."""
        return self._dispatch_to_mpf("changed_lamps")

    def ChangedGIStrings(self):
        """Return a list of changed GI strings."""
        return self._dispatch_to_mpf("changed_gi_strings")

    def ChangedLEDs(self):
        """Return a list of changed lamps."""
        return self._dispatch_to_mpf("changed_leds")
        
    def ChangedBrightnessLEDs(self):
        """Return a list of changed LEDs with brightness vlaues as floats."""
        return self._dispatch_to_mpf("changed_brightness_leds")
        
    def ChangedFlashers(self):
        """Return a list of changed GI strings."""
        return self._dispatch_to_mpf("changed_flashers")

    def HardwareRules(self):
        """Return a list of MPF Hardware Rules for autofire coils."""
        return self._dispatch_to_mpf("get_hardwarerules")

    def IsCoilActive(self, number):
        """Return True if a MPF Hardware Rule for the coil(number) exists."""
        return self._dispatch_to_mpf("get_coilactive", number=number)


def Register(pyclass=Controller, p_game=None):
    """ Registration code for the Visual Pinball COM interface for pyprocgame."""
    pythoncom.CoInitialize()
    from win32com.server.register import UseCommandLine
    UseCommandLine(pyclass)


# Run the registration code by default.  Using the commandline param
# "--unregister" will unregister this COM object.

def main():
    if not win32com:
        raise AssertionError("Please run: pip3 install pywin32")
    Register(Controller)