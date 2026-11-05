# WebSocket 处理程序

通过定义 `SOCKET` 处理 `.py` 路由文件中的 WebSocket 连接。

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## 规则

- URL是文件路径，与[routing](../../README.md)相同。
- 只有 `.py` 路由文件通过 `SOCKET` 注册 WebSocket 处理程序。
- 确保您的反向代理转发 WebSocket 升级请求。

## 后续步骤

- [API](../handlers/README.md)：同一文件中的 HTTP 处理程序
- [部署](../../../deployment/README.md)：代理配置
- 控制器上的[模块化路由](../../modular/README.md)：`SOCKET`
