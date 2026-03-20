import os
import unittest
from unittest.mock import call, MagicMock, mock_open, patch

from ntk import conf
from ntk.conf import Config


class TestTailwindDetection(unittest.TestCase):
    """Tests for Tailwind CSS auto-detection in Config."""

    @patch("os.path.exists", autospec=True)
    @patch("yaml.load", autospec=True)
    def setUp(self, mock_load_yaml, mock_patch_exists):
        mock_patch_exists.return_value = True
        mock_load_yaml.return_value = {
            'development': {
                'apikey': 'abc123',
                'store': 'https://test.com',
                'theme_id': 1
            }
        }
        with patch('builtins.open', mock_open(read_data='yaml data')):
            self.config = Config()

    def test_detect_tailwind_returns_false_when_no_input_file(self):
        """Should return False when css/input.css doesn't exist."""
        with patch('os.path.exists', return_value=False):
            result = self.config.detect_tailwind()
        self.assertFalse(result)

    def test_detect_tailwind_v4_with_marker(self):
        """Should detect Tailwind v4 when input.css contains @import 'tailwindcss'."""
        def exists_side_effect(path):
            if path == conf.TAILWIND_INPUT:
                return True
            if path == './tailwindcss':
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect), \
             patch('os.path.isfile', return_value=True), \
             patch('os.access', return_value=True), \
             patch('builtins.open', mock_open(read_data='@import "tailwindcss";\n@theme {}')):
            result = self.config.detect_tailwind()

        self.assertTrue(result)
        self.assertEqual(self.config.tailwind_input, conf.TAILWIND_INPUT)
        self.assertEqual(self.config.tailwind_output, conf.TAILWIND_OUTPUT)
        self.assertEqual(self.config.tailwind_binary, './tailwindcss')

    def test_detect_tailwind_returns_false_without_binary(self):
        """Should return False when input.css exists but no binary found."""
        def exists_side_effect(path):
            if path == conf.TAILWIND_INPUT:
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect), \
             patch('os.path.isfile', return_value=False), \
             patch('shutil.which', return_value=None), \
             patch('builtins.open', mock_open(read_data='@import "tailwindcss";')):
            result = self.config.detect_tailwind()

        self.assertFalse(result)

    def test_detect_tailwind_finds_system_binary(self):
        """Should find tailwindcss on PATH via shutil.which."""
        def exists_side_effect(path):
            if path == conf.TAILWIND_INPUT:
                return True
            if path.startswith('./'):
                return False
            return False

        with patch('os.path.exists', side_effect=exists_side_effect), \
             patch('os.path.isfile', return_value=False), \
             patch('shutil.which', side_effect=lambda b: '/usr/local/bin/tailwindcss' if b == 'tailwindcss' else None), \
             patch('builtins.open', mock_open(read_data='@import "tailwindcss";')):
            result = self.config.detect_tailwind()

        self.assertTrue(result)
        self.assertEqual(self.config.tailwind_binary, 'tailwindcss')

    def test_detect_tailwind_skips_when_already_configured(self):
        """Should return True immediately when binary and input are already set."""
        self.config.tailwind_input = 'css/input.css'
        self.config.tailwind_binary = './tailwindcss'
        result = self.config.detect_tailwind()
        self.assertTrue(result)

    def test_detect_sass_compat(self):
        """Should detect scripts/sass-compat.py when present."""
        def exists_side_effect(path):
            if path == conf.TAILWIND_INPUT:
                return True
            if path == './tailwindcss':
                return True
            if path == conf.TAILWIND_SASS_COMPAT:
                return True
            return False

        with patch('os.path.exists', side_effect=exists_side_effect), \
             patch('os.path.isfile', return_value=True), \
             patch('os.access', return_value=True), \
             patch('builtins.open', mock_open(read_data='@import "tailwindcss";')):
            self.config.detect_tailwind()

        self.assertEqual(self.config.tailwind_sass_compat, conf.TAILWIND_SASS_COMPAT)

    def test_read_config_with_tailwind_section(self):
        """Should read tailwind config from config.yml."""
        yaml_data = {
            'development': {
                'apikey': 'abc123',
                'store': 'https://test.com',
                'theme_id': 1,
                'tailwind': {
                    'input': 'src/input.css',
                    'output': 'dist/main.css',
                    'binary': '/usr/local/bin/tailwindcss',
                    'sass_compat': 'tools/compat.py'
                }
            }
        }
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='yaml')), \
             patch('yaml.load', return_value=yaml_data):
            config = Config()

        self.assertEqual(config.tailwind_input, 'src/input.css')
        self.assertEqual(config.tailwind_output, 'dist/main.css')
        self.assertEqual(config.tailwind_binary, '/usr/local/bin/tailwindcss')
        self.assertEqual(config.tailwind_sass_compat, 'tools/compat.py')

    def test_read_config_tailwind_defaults(self):
        """Should use defaults when tailwind section has partial config."""
        yaml_data = {
            'development': {
                'apikey': 'abc123',
                'store': 'https://test.com',
                'theme_id': 1,
                'tailwind': {}
            }
        }
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data='yaml')), \
             patch('yaml.load', return_value=yaml_data):
            config = Config()

        self.assertEqual(config.tailwind_input, conf.TAILWIND_INPUT)
        self.assertEqual(config.tailwind_output, conf.TAILWIND_OUTPUT)


class TestTailwindCompile(unittest.TestCase):
    """Tests for Tailwind CSS compilation in Command."""

    @patch("os.path.exists", autospec=True)
    @patch("yaml.load", autospec=True)
    @patch('ntk.command.Gateway', autospec=True)
    def setUp(self, mock_gateway, mock_load_yaml, mock_patch_exists):
        mock_patch_exists.return_value = True
        mock_load_yaml.return_value = {
            'development': {
                'apikey': 'abc123',
                'store': 'https://test.com',
                'theme_id': 1
            }
        }
        config = {
            'env': 'development',
            'apikey': 'abc123',
            'theme_id': 1,
            'store': 'https://test.com',
        }
        with patch('builtins.open', mock_open(read_data='yaml data')):
            from ntk.command import Command
            self.parser = MagicMock(**config)
            self.command = Command()
            self.mock_gateway = mock_gateway

    @patch('ntk.command.subprocess.run')
    def test_compile_tailwind_success(self, mock_run):
        """Should compile successfully and return True."""
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './tailwindcss'
        self.command.config.tailwind_sass_compat = None

        mock_run.return_value = MagicMock(returncode=0, stderr='', stdout='')

        with patch.object(self.command.config, 'detect_tailwind', return_value=True):
            result = self.command._compile_tailwind()

        self.assertTrue(result)
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        self.assertIn('./tailwindcss', call_args[0][0])

    @patch('ntk.command.subprocess.run')
    def test_compile_tailwind_with_minify(self, mock_run):
        """Should pass --minify flag when requested."""
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './tailwindcss'
        self.command.config.tailwind_sass_compat = None

        mock_run.return_value = MagicMock(returncode=0, stderr='', stdout='')

        with patch.object(self.command.config, 'detect_tailwind', return_value=True):
            result = self.command._compile_tailwind(minify=True)

        self.assertTrue(result)
        cmd_args = mock_run.call_args[0][0]
        self.assertIn('--minify', cmd_args)

    @patch('ntk.command.subprocess.run')
    def test_compile_tailwind_failure(self, mock_run):
        """Should return False when compilation fails."""
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './tailwindcss'
        self.command.config.tailwind_sass_compat = None

        mock_run.return_value = MagicMock(returncode=1, stderr='Error: invalid CSS', stdout='')

        with patch.object(self.command.config, 'detect_tailwind', return_value=True):
            result = self.command._compile_tailwind()

        self.assertFalse(result)

    def test_compile_tailwind_no_detection(self):
        """Should return False when Tailwind is not detected."""
        with patch.object(self.command.config, 'detect_tailwind', return_value=False):
            result = self.command._compile_tailwind()

        self.assertFalse(result)

    @patch('ntk.command.subprocess.run')
    def test_compile_tailwind_binary_not_found(self, mock_run):
        """Should return False and log error when binary is missing."""
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './missing-tailwindcss'
        self.command.config.tailwind_sass_compat = None

        mock_run.side_effect = FileNotFoundError('No such file')

        with patch.object(self.command.config, 'detect_tailwind', return_value=True):
            result = self.command._compile_tailwind()

        self.assertFalse(result)

    @patch('ntk.command.subprocess.run')
    def test_compile_tailwind_timeout(self, mock_run):
        """Should return False when compilation times out."""
        import subprocess
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './tailwindcss'
        self.command.config.tailwind_sass_compat = None

        mock_run.side_effect = subprocess.TimeoutExpired(cmd='./tailwindcss', timeout=60)

        with patch.object(self.command.config, 'detect_tailwind', return_value=True):
            result = self.command._compile_tailwind()

        self.assertFalse(result)

    @patch('ntk.command.subprocess.run')
    def test_compile_tailwind_runs_sass_compat(self, mock_run):
        """Should run sass-compat.py after successful compilation."""
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './tailwindcss'
        self.command.config.tailwind_sass_compat = 'scripts/sass-compat.py'

        mock_run.return_value = MagicMock(returncode=0, stderr='', stdout='')

        with patch.object(self.command.config, 'detect_tailwind', return_value=True), \
             patch('os.path.exists', return_value=True):
            result = self.command._compile_tailwind()

        self.assertTrue(result)
        # Should be called twice: once for tailwind, once for sass-compat
        self.assertEqual(mock_run.call_count, 2)

    @patch('ntk.command.subprocess.run')
    def test_compile_tailwind_sass_compat_failure(self, mock_run):
        """Should return False when sass-compat.py fails."""
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './tailwindcss'
        self.command.config.tailwind_sass_compat = 'scripts/sass-compat.py'

        # First call (tailwind) succeeds, second call (sass-compat) fails
        mock_run.side_effect = [
            MagicMock(returncode=0, stderr='', stdout=''),
            MagicMock(returncode=1, stderr='sass-compat error', stdout=''),
        ]

        with patch.object(self.command.config, 'detect_tailwind', return_value=True), \
             patch('os.path.exists', return_value=True):
            result = self.command._compile_tailwind()

        self.assertFalse(result)


class TestTailwindWatch(unittest.TestCase):
    """Tests for Tailwind watch subprocess management."""

    @patch("os.path.exists", autospec=True)
    @patch("yaml.load", autospec=True)
    @patch('ntk.command.Gateway', autospec=True)
    def setUp(self, mock_gateway, mock_load_yaml, mock_patch_exists):
        mock_patch_exists.return_value = True
        mock_load_yaml.return_value = {
            'development': {
                'apikey': 'abc123',
                'store': 'https://test.com',
                'theme_id': 1
            }
        }
        with patch('builtins.open', mock_open(read_data='yaml data')):
            from ntk.command import Command
            self.command = Command()

    @patch('ntk.command.subprocess.Popen')
    def test_start_tailwind_watch(self, mock_popen):
        """Should start Tailwind CLI in watch mode."""
        self.command.config.tailwind_input = 'css/input.css'
        self.command.config.tailwind_output = 'assets/main.css'
        self.command.config.tailwind_binary = './tailwindcss'

        mock_process = MagicMock()
        mock_popen.return_value = mock_process

        with patch.object(self.command.config, 'detect_tailwind', return_value=True):
            result = self.command._start_tailwind_watch()

        self.assertEqual(result, mock_process)
        call_args = mock_popen.call_args[0][0]
        self.assertIn('--watch', call_args)

    def test_start_tailwind_watch_no_detection(self):
        """Should return None when Tailwind is not detected."""
        with patch.object(self.command.config, 'detect_tailwind', return_value=False):
            result = self.command._start_tailwind_watch()

        self.assertIsNone(result)

    def test_stop_tailwind_watch(self):
        """Should terminate the Tailwind watch process."""
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process still running

        self.command._stop_tailwind_watch(mock_process)

        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once_with(timeout=5)

    def test_stop_tailwind_watch_already_stopped(self):
        """Should not terminate if process already stopped."""
        mock_process = MagicMock()
        mock_process.poll.return_value = 0  # Already stopped

        self.command._stop_tailwind_watch(mock_process)

        mock_process.terminate.assert_not_called()

    def test_stop_tailwind_watch_none(self):
        """Should handle None process gracefully."""
        self.command._stop_tailwind_watch(None)  # Should not raise


if __name__ == '__main__':
    unittest.main()
