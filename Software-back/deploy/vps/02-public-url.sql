UPDATE system_config SET config_value = 'https://zhanhui.cloud/walle/api'
  WHERE config_key = 'api.base-url' AND config_value = 'https://zhanhui.cloud:8443/api';
UPDATE system_config SET config_value = 'https://zhanhui.cloud/walle'
  WHERE config_key = 'static.base-url' AND config_value = 'https://zhanhui.cloud:8443';
UPDATE system_config SET config_value = 'https://zhanhui.cloud'
  WHERE config_key = 'socket.server-url' AND config_value = 'https://zhanhui.cloud:8443';
UPDATE system_config SET config_value = 'https://zhanhui.cloud/walle'
  WHERE config_key = 'web.base-url' AND config_value = 'http://localhost:5173';
