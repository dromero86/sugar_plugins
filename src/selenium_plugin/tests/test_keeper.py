"""
Tests de la capa keeper y del SessionController (Fases 2 y 3)
=============================================================

Verifican transporte, servidor, cliente, registry y controller sin
levantar un navegador real.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from kernel.contract import SessionSpec
from keeper.transport import LocalTransport
from keeper.KeeperServer import KeeperServer
from keeper.KeeperClient import KeeperClient
from keeper import registry
from session.SessionController import SessionController, InProcessBackend, DetachedBackend


class FakeSession:
    def __init__(self):
        self.driver = None
        self.ensured = 0
        self.executed = []
        self.quit_called = 0

    def ensure_driver(self, spec):
        self.ensured += 1
        self.driver = Mock()
        return self.driver

    def execute_command(self, command, config):
        self.executed.append((command, config))
        return {'command': command, 'success': True}

    def quit(self):
        self.quit_called += 1


class TestLocalTransport(unittest.TestCase):
    def test_request_response_roundtrip(self):
        transport = LocalTransport()
        transport.send_request({'id': 1, 'op': 'ping'})
        self.assertEqual(transport.next_request(timeout=1)['op'], 'ping')
        transport.send_response({'id': 1, 'ok': True})
        self.assertTrue(transport.next_response(timeout=1)['ok'])


class TestKeeperServer(unittest.TestCase):
    def _server(self):
        session = FakeSession()
        server = KeeperServer(SessionSpec.from_meta({'browser': 'firefox'}), session=session)
        server.start()
        server.wait_ready(timeout=5)
        return server, session, KeeperClient(server)

    def test_execute_roundtrip(self):
        server, session, client = self._server()
        result = client.execute('open', {'url': 'https://example.com'})
        self.assertEqual(result['command'], 'open')
        self.assertEqual(session.executed, [('open', {'url': 'https://example.com'})])

    def test_detach_keeps_session_alive(self):
        server, session, client = self._server()
        client.detach()
        self.assertEqual(session.quit_called, 0)
        self.assertTrue(server.is_alive())

    def test_quit_closes_session(self):
        server, session, client = self._server()
        client.quit()
        server.join(timeout=5)
        self.assertEqual(session.quit_called, 1)
        self.assertFalse(server.is_alive())

    def test_ready_propagates_init_error(self):
        class FailingSession(FakeSession):
            def ensure_driver(self, spec):
                raise RuntimeError('boom')

        server = KeeperServer(SessionSpec.from_meta({'browser': 'firefox'}), session=FailingSession())
        server.start()
        with self.assertRaises(RuntimeError):
            server.wait_ready(timeout=5)


class FakeServer:
    def __init__(self, spec, plugin_name='SeleniumKeeper'):
        self.spec = spec
        self.plugin_name = plugin_name
        self.transport = LocalTransport()

    def start(self):
        pass

    def wait_ready(self, timeout=60):
        pass


class TestRegistry(unittest.TestCase):
    def setUp(self):
        registry._KEEPERS.clear()

    def test_reuses_keeper_for_same_spec(self):
        spec = SessionSpec.from_meta({'browser': 'firefox'})
        with patch('keeper.registry.KeeperServer', FakeServer):
            first = registry.get_or_create(spec)
            second = registry.get_or_create(spec)
        self.assertIs(first, second)

    def test_creates_new_keeper_for_different_spec(self):
        with patch('keeper.registry.KeeperServer', FakeServer):
            a = registry.get_or_create(SessionSpec.from_meta({'browser': 'firefox'}))
            b = registry.get_or_create(SessionSpec.from_meta({'browser': 'chrome'}))
        self.assertIsNot(a, b)
        self.assertEqual(len(registry.active_keys()), 2)

    def test_remove(self):
        spec = SessionSpec.from_meta({'browser': 'firefox'})
        with patch('keeper.registry.KeeperServer', FakeServer):
            registry.get_or_create(spec)
            registry.remove(spec)
        self.assertEqual(registry.active_keys(), [])


class TestSessionController(unittest.TestCase):
    def test_inprocess_delegates(self):
        session = FakeSession()
        controller = SessionController(session, 'T')
        spec = SessionSpec.from_meta({'browser': 'firefox'})
        controller.configure(spec)
        controller.ensure(spec)
        result = controller.execute('open', {'url': 'x'})
        self.assertFalse(controller.is_detached)
        self.assertEqual(session.ensured, 1)
        self.assertEqual(result['command'], 'open')
        controller.cleanup()
        self.assertEqual(session.quit_called, 1)

    def test_detached_uses_registry_and_keeps_browser(self):
        fake_client = Mock()
        fake_client.execute.return_value = {'ok': True}
        with patch('keeper.registry.get_or_create', return_value=fake_client) as get:
            controller = SessionController(FakeSession(), 'T')
            spec = SessionSpec.from_meta({'browser': 'firefox', 'detach': True})
            controller.configure(spec)
            controller.ensure(spec)
            self.assertTrue(controller.is_detached)
            self.assertEqual(controller.execute('open', {'url': 'x'}), {'ok': True})
            controller.cleanup()
        get.assert_called_once()
        fake_client.detach.assert_called_once()
        fake_client.quit.assert_not_called()

    def test_detached_quit_closes_and_removes_keeper(self):
        fake_client = Mock()
        with patch('keeper.registry.get_or_create', return_value=fake_client), \
             patch('keeper.registry.remove') as remove:
            controller = SessionController(FakeSession(), 'T')
            spec = SessionSpec.from_meta({'browser': 'firefox', 'detach': True})
            controller.configure(spec)
            controller.ensure(spec)
            result = controller.execute('quit', {'id': 'q'})
        self.assertEqual(result, {'q': True, 'success': True})
        fake_client.quit.assert_called_once()
        remove.assert_called_once()


if __name__ == '__main__':
    unittest.main()
