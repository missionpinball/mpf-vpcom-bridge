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
    def test_VpCom(self, pythoncom):
        import register_vpcom
        vpcom = register_vpcom.Controller(loop=self.loop)
        vpcom._connect = MagicMock()
        vpcom._raise_error = self._error

        vpcom.bcp_client = self._bcp_external_client

        vpcom.Run()
        self.advance_time_and_run()
        self.init.result()

        self.assertFalse(vpcom.Switch(3))
        self.assertFalse(vpcom.GetSwitch(3))
        vpcom.SetSwitch(3, True)
        self.assertTrue(vpcom.Switch(3))
        self.assertTrue(vpcom.GetSwitch(3))
        vpcom.SetSwitch(3, False)
        self.assertFalse(vpcom.Switch(3))
        self.assertFalse(vpcom.GetSwitch(3))

        self.assertSwitchState("s_test00", False)
        self.assertSwitchState("s_test37", False)
        self.assertSwitchState("s_test77_nc", True)

        vpcom.SetSwitch(1, True)
        self.assertSwitchState("s_test00", True)
        self.assertSwitchState("s_test37", False)
        self.assertSwitchState("s_test77_nc", True)

        self.assertFalse(vpcom.ChangedSolenoids())
        self.machine.coils["c_test"].pulse()
        self.machine.coils["c_test_allow_enable"].enable()
        self.assertCountEqual([(0, True), (1, True)], vpcom.ChangedSolenoids())
        self.advance_time_and_run(.1)
        self.assertCountEqual([(0, False)], vpcom.ChangedSolenoids())
        self.machine.coils["c_test_allow_enable"].disable()
        self.assertCountEqual([(1, False)], vpcom.ChangedSolenoids())

        self.assertFalse(vpcom.ChangedLamps())
        self.assertFalse(vpcom.ChangedGIStrings())
        self.machine.lights["test_light"].on()
        self.machine.lights["test_gi"].on()
        self.assertCountEqual([(3, True)], vpcom.ChangedLamps())
        self.assertCountEqual([(15, True)], vpcom.ChangedGIStrings())
        self.machine.lights["test_light"].off()
        self.assertCountEqual([(3, False)], vpcom.ChangedLamps())
