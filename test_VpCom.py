from unittest.mock import patch, MagicMock

from mpf.tests.MpfBcpTestCase import MpfBcpTestCase


class TestVPCom(MpfBcpTestCase):

    def setUp(self):
        super().setUp()
        # we are connected as anonymous client
        self._bcp_client.name = None

    @patch("register_vpcom.pythoncom")
    def test_VpCom(self, pythoncom):
        import register_vpcom
        vpcom = register_vpcom.Controller(loop=self.loop)
        vpcom._connect = MagicMock()

        vpcom.bcp_client = self._bcp_external_client

        vpcom.Run()
        vpcom.Switch(17)
        vpcom.SetSwitch(17, True)

