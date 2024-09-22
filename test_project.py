import unittest
from unittest.mock import patch, MagicMock
from tcp_client import get_firmware_version, probe_ssl_support
from network_scanner import scan_network
import socket
import ssl
import time

config = {
            'tcp_settings': {
                'port': 12345,
                'retries': 3,
                'use_ssl': True
            }
        }

class TestTCPClient(unittest.TestCase):
    @patch('socket.create_connection')
    def test_get_firmware_version_ssl_fallback(self, mock_create_connection):
        # Mock the socket connection and SSL failure
        mock_sock = MagicMock()
        mock_create_connection.return_value = mock_sock
        mock_sock.recv.return_value = b"1.0.3"

        with patch('ssl.create_default_context') as mock_ssl:
            mock_ssl.return_value.wrap_socket.side_effect = ssl.SSLError
            firmware = get_firmware_version('192.168.1.5', config)
            self.assertEqual(firmware, "1.0.3")  # Should fallback to non-SSL and succeed

    @patch('socket.create_connection')
    def test_get_firmware_version_timing(self, mock_create_connection):
        # Mock the socket connection and data with timing
        mock_sock = MagicMock()
        mock_create_connection.return_value = mock_sock
        mock_sock.recv.return_value = b"1.0.3"

        start_time = time.time()
        firmware = get_firmware_version('192.168.1.5', config)
        elapsed_time = time.time() - start_time

        self.assertEqual(firmware, "1.0.3")
        self.assertLess(elapsed_time, 5)  # Expect the query to take less than 5 seconds

    @patch('socket.create_connection')
    def test_probe_ssl_support(self, mock_create_connection):
        # Mock SSL support
        mock_sock = MagicMock()
        mock_create_connection.return_value = mock_sock
        
        with patch('ssl.create_default_context') as mock_ssl:
            mock_ssl.return_value.wrap_socket.return_value = mock_sock
            self.assertTrue(probe_ssl_support('192.168.1.5', 12345))

    @patch('socket.create_connection')
    def test_probe_ssl_support_failure(self, mock_create_connection):
        # Mock failure of SSL handshake
        mock_create_connection.side_effect = ssl.SSLError
        
        with patch('ssl.create_default_context') as mock_ssl:
            self.assertFalse(probe_ssl_support('192.168.1.5', 12345))

    @patch('socket.create_connection')
    def test_get_firmware_version_advanced_error_handling(self, mock_create_connection):
        # Mock the socket connection and a timeout error
        mock_create_connection.side_effect = socket.timeout

        firmware = get_firmware_version('192.168.1.5', config)
        self.assertIsNone(firmware)

if __name__ == '__main__':
    unittest.main()
