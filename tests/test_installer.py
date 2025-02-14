from unittest.case import TestCase
from unittest.mock import patch

from ntk.installer import auto_install_and_generate_ntk_command


class TestInstaller(TestCase):
    def test_auto_install_and_generate_ntk_command_should_call_subprocess_and_os_correctly(self):
        with patch("subprocess.run") as mock_subprocess, patch("os.system") as mock_os:
            auto_install_and_generate_ntk_command()

            mock_subprocess.assert_called_with(['python', '-m', 'pip', 'install', 'next-theme-kit', "--upgrade"])

            mock_os.assert_any_call("doskey ntk=python -m ntk $*")

            mock_os.assert_any_call("cmd /k")
