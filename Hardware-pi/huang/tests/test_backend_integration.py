import importlib.util
import os
import pathlib
import sys
import threading
import types
import unittest
from unittest.mock import Mock, patch

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dependencies():
    config = load('huang_config_test', 'config.py')
    requests = types.ModuleType('requests')
    shared = types.ModuleType('shared')
    shared.shutdown_event = threading.Event()
    shared.state = Mock()
    ui = types.ModuleType('ui')
    ui.update_ui = Mock()
    voice = types.ModuleType('voice_player')
    voice.play_cloud_voice = Mock()
    return config, requests, shared, {'config': config, 'requests': requests, 'shared': shared,
                                       'ui': ui, 'voice_player': voice}


class BackendIntegrationTest(unittest.TestCase):
    def test_onenet_and_backend_tokens_are_separate(self):
        with patch.dict(os.environ, {'WALLE_DEVICE_API_TOKEN': 'backend-secret',
                                    'WALLE_ONENET_TOKEN': 'onenet-secret'}, clear=True):
            config = load('huang_secrets_test', 'config.py')
            self.assertEqual(config.WALLE_DEVICE_API_TOKEN, 'backend-secret')
            self.assertEqual(config.TOKEN, 'onenet-secret')

    def test_health_upload_uses_device_token_and_canonical_id(self):
        with patch.dict(os.environ, {'WALLE_DEVICE_API_TOKEN': 'device-secret'}):
            config, requests, shared, modules = dependencies()
            with patch.dict(sys.modules, modules):
                manager = load('huang_mqtt_test', 'mqtt_manager.py')
                self.assertEqual(manager.DEVICE_ID, 'WALLE_1')
                self.assertEqual(manager._headers(), {'X-Walle-Device-Token': 'device-secret'})
                requests.post = Mock(return_value=Mock(status_code=200))
                manager.post_health_data('addRate', 'rate', 70)
                args, kwargs = requests.post.call_args
                self.assertEqual(args[0], 'https://zhanhui.cloud/walle/api/healthy/addRate')
                self.assertEqual(kwargs['json']['deviceId'], 'WALLE_1')
                self.assertEqual(kwargs['headers']['X-Walle-Device-Token'], 'device-secret')

    def test_event_sync_uses_device_token_without_signing_key(self):
        with patch.dict(os.environ, {'WALLE_DEVICE_API_TOKEN': 'device-secret'}, clear=True):
            config, requests, shared, modules = dependencies()
            requests.get = Mock(return_value=Mock(status_code=200, json=lambda: {'code': 1, 'data': {'rows': [{'id': 9}]}}))
            with patch.dict(sys.modules, modules):
                manager = load('huang_mqtt_event_test', 'mqtt_manager.py')
                self.assertEqual(manager._fetch_pending_events(), [{'id': 9}])
                args, kwargs = requests.get.call_args
                self.assertEqual(args[0], 'https://zhanhui.cloud/walle/api/device/events/WALEE_1')
                self.assertEqual(kwargs['headers']['X-Walle-Device-Token'], 'device-secret')
                self.assertNotIn('token', kwargs['headers'])

    def test_demo_health_values_remain_available_without_sensors(self):
        camera = types.ModuleType('camera_manager')
        with patch.dict(sys.modules, {'camera_manager': camera}), patch('time.time', return_value=100.0):
            shared = load('huang_shared_test', 'shared.py')
            state = shared.RobotState()
            snapshot = state.health_snapshot()
            self.assertGreater(snapshot['temperature'], 0)
            self.assertGreater(snapshot['humidity'], 0)
            self.assertGreater(snapshot['nearlink']['hr'], 0)
            self.assertGreater(snapshot['nearlink']['br'], 0)

    def test_remote_control_join_authenticates_the_robot(self):
        with patch.dict(os.environ, {'WALLE_DEVICE_API_TOKEN': 'device-secret'}):
            config, _, _, modules = dependencies()
            class DummySocket:
                def __init__(self):
                    self.emit = Mock()
                def on(self, event):
                    return lambda fn: fn
            socketio = types.ModuleType('socketio')
            socketio.Client = lambda **kwargs: DummySocket()
            camera = types.ModuleType('camera_pusher')
            camera.start_camera_pusher = Mock()
            modules.update({'socketio': socketio, 'camera_pusher': camera})
            with patch.dict(sys.modules, modules):
                controller = load('huang_socket_test', 'socketio_controller.py')
                controller.on_connect()
                controller.sio.emit.assert_called_once_with(
                    'join', {'room': 'robot_WALEE_1', 'deviceToken': 'device-secret'})
                self.assertEqual(controller.SOCKETIO_SERVER_URL, 'https://zhanhui.cloud')

    def test_remote_tts_passes_text_as_an_argument_without_a_shell(self):
        with patch.dict(os.environ, {'WALLE_DEVICE_API_TOKEN': 'device-secret'}):
            config, _, _, modules = dependencies()
            class DummySocket:
                def on(self, event): return lambda fn: fn
            socketio = types.ModuleType('socketio')
            socketio.Client = lambda **kwargs: DummySocket()
            camera = types.ModuleType('camera_pusher')
            camera.start_camera_pusher = Mock()
            modules.update({'socketio': socketio, 'camera_pusher': camera})
            with patch.dict(sys.modules, modules):
                controller = load('huang_socket_tts_test', 'socketio_controller.py')
                with patch('subprocess.run') as run:
                    controller._play_tts('hello; echo unsafe')
                    args, kwargs = run.call_args_list[0]
                    self.assertIsInstance(args[0], list)
                    self.assertIn('hello; echo unsafe', args[0])
                    self.assertFalse(kwargs.get('shell', False))

    def test_remote_join_rejection_is_visible_in_logs(self):
        config, _, _, modules = dependencies()
        class DummySocket:
            def on(self, event): return lambda fn: fn
        socketio = types.ModuleType('socketio')
        socketio.Client = lambda **kwargs: DummySocket()
        camera = types.ModuleType('camera_pusher')
        camera.start_camera_pusher = Mock()
        modules.update({'socketio': socketio, 'camera_pusher': camera})
        with patch.dict(sys.modules, modules):
            controller = load('huang_socket_auth_test', 'socketio_controller.py')
            with self.assertLogs('SocketIO', level='ERROR') as logs:
                controller.on_join_error({'message': 'unauthorized'})
            self.assertIn('unauthorized', logs.output[0])

    def test_camera_push_rejects_stale_shared_frames(self):
        config, _, shared, modules = dependencies()
        camera_manager = types.ModuleType('camera_manager')
        camera_manager.is_camera_ready = Mock(return_value=False)
        cv2 = types.ModuleType('cv2')
        modules.update({'cv2': cv2, 'camera_manager': camera_manager})
        with patch.dict(sys.modules, modules):
            pusher = load('huang_camera_push_test', 'camera_pusher.py')
            self.assertIsNone(pusher.current_frame())
            shared.state.get_camera_frame.assert_not_called()
            camera_manager.is_camera_ready.return_value = True
            self.assertIs(pusher.current_frame(), shared.state.get_camera_frame.return_value)


if __name__ == '__main__':
    unittest.main()
