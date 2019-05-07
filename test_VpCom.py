import asyncio
import os
from unittest.mock import patch, MagicMock

from mpf.core.utility_functions import Util
from mpf.tests.MpfBcpTestCase import MpfBcpTestCase

class TestVPCom(MpfBcpTestCase):

    def get_platform(self):
        return False

    def getConfigFile(self):
        return 'config.yaml'

    def getMachinePath(self):
        def getconfigFile(self):
            return 'config.yaml'
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_config')

    def _initialise_machine(self):
        self.init = Util.ensure_future(self.machine.initialise(), loop=self.machine.clock.loop)
        self.advance_time_and_run(1)

        with self.assertRaises(asyncio.futures.InvalidStateError):
            self.init.result()

    def setUp(self):
        super().setUp()
        # we are connected as anonymous client
        self._bcp_client.name = None

    def _error(self, desc):
        raise AssertionError(desc)

    @patch("register_vpcom.pythoncom")
    def test_vpcom(self, pythoncom):

        import register_vpcom
        vpcom = register_vpcom.Controller(loop=self.loop)
        vpcom._connect = MagicMock()
        vpcom._raise_error = self._error

        vpcom.bcp_client = self._bcp_external_client

        vpcom.Run()
        self.advance_time_and_run()
        self.init.result()

        # Switch Test
        #  s_test00: 1
        #  s_test37: 2
        #  s_test77_nc: 3
        #  s_top_a: swa

        vpcom.SetSwitch(2, False)
        self.assertFalse(vpcom.Switch(2))
        self.assertFalse(vpcom.GetSwitch(2))
        self.assertSwitchState("s_test37", False)
        vpcom.SetSwitch(2, True)
        self.assertTrue(vpcom.Switch(2))
        self.assertTrue(vpcom.GetSwitch(2))
        self.assertSwitchState("s_test37", True)
        vpcom.SetSwitch(2, False)
        self.assertFalse(vpcom.Switch(2))
        self.assertFalse(vpcom.GetSwitch(2))
        self.assertSwitchState("s_test37", False)

        vpcom.SetSwitch(1, False)
        self.assertSwitchState("s_test00", False)
        self.assertSwitchState("s_test37", False)
        vpcom.SetSwitch(1, True)
        self.assertSwitchState("s_test00", True)
        self.assertSwitchState("s_test37", False)

        #String type numbers
        vpcom.SetSwitch("swa", False)
        self.assertSwitchState("s_top_a", False)
        self.assertFalse(vpcom.Switch("swa"))
        vpcom.SetSwitch("swa", True)
        self.assertSwitchState("s_top_a", True)
        self.assertTrue(vpcom.GetSwitch("swa"))
        vpcom.PulseSW("swa")
        self.assertSwitchState("s_top_a", False)
        self.assertFalse(vpcom.Switch("swa"))

        #Switch(3) is NC
        vpcom.SetSwitch(3, False)
        self.assertTrue(vpcom.Switch(3))
        self.assertTrue(vpcom.GetSwitch(3))
        self.assertSwitchState("s_test77_nc", True)
        vpcom.SetSwitch(3, True)
        self.assertFalse(vpcom.Switch(3))
        self.assertFalse(vpcom.GetSwitch(3))
        self.assertSwitchState("s_test77_nc", False)
        vpcom.SetSwitch(3, False)
        self.assertTrue(vpcom.Switch(3))
        self.assertTrue(vpcom.GetSwitch(3))
        self.assertSwitchState("s_test77_nc", True)

        #Solenoid Test
        #  c_test: 0
        #  c_test_allow_enable: 1
        #  c_trough_eject: coil2

        #Pulse and Enable, both should be ON
        self.assertFalse(vpcom.ChangedSolenoids())
        self.machine.coils["c_test"].pulse()
        self.machine.coils["c_trough_eject"].pulse()
        self.machine.coils["c_test_allow_enable"].enable()
        self.assertCountEqual([("0", True),("1", True),("coil2", True)], vpcom.ChangedSolenoids())

        #After a short while the pulsed coils should be OFF
        self.advance_time_and_run(.1)
        self.assertCountEqual([("0", False),("coil2", False)], vpcom.ChangedSolenoids())

        #Disable to get hold coil OFF
        self.machine.coils["c_test_allow_enable"].disable()
        self.assertCountEqual([("1", False)], vpcom.ChangedSolenoids())

        #Lights Test
        #  test_light: lamp3
        #  test_light2: 15
        #  test_gi: 15

        self.assertFalse(vpcom.ChangedLamps())
        self.assertFalse(vpcom.ChangedGIStrings())
        self.machine.lights["test_light"].on()
        self.machine.lights["test_gi"].on()
        self.assertCountEqual([("lamp3", True)], vpcom.ChangedLamps())
        self.assertCountEqual([("15", True)], vpcom.ChangedGIStrings())
        self.machine.lights["test_light"].off()
        self.assertCountEqual([("lamp3", False)], vpcom.ChangedLamps())

        #Hardwarerules Test
        # Game Over
        # no rules are active
        self.assertFalse(vpcom.HardwareRules())
        self.assertFalse(vpcom.IsCoilActive("0"))

        # Start Game
        self.machine_config_patches['switches'] = dict()
        self.machine_config_patches['switches']['s_start'] = {"number": "", "tags": "start"}
        for trough in self.machine.ball_devices.items_tagged("trough"):
            for switch in trough.config['ball_switches']:
                self.hit_switch_and_run(switch.name, 0)
        self.advance_time_and_run(1)

        # Game still OFF
        self.assertIsNone(self.machine.game, "Expected game to have ended but game is active.")

        self.hit_and_release_switch("s_start")
        self.advance_time_and_run(1)

        # Game is now started
        self.assertIsNotNone(self.machine.game, "Expected a running game but no game is active.")
        self.assertEqual(1, self.machine.game.num_players)

        #rules for autofire_coils are active
        self.assertTrue(vpcom.IsCoilActive("0"))
        self.assertTrue(vpcom.HardwareRules())
