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

        vpcom.Switch(17)
        vpcom.SetSwitch(17, True)

