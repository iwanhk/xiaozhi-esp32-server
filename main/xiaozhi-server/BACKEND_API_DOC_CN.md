# 小智后端服务接口说明

本文档旨在为开发者提供与“小智 ESP32 服务”后端进行交互的详细指南。

> ### **全局参数说明**
>
> 根据最新要求，所有向后端发起的请求接口（包括 WebSocket 消息和 HTTP API）都增加了一个 `position` 参数，用于传递用户当前的地理位置。该参数结构如下，包含两个整数值 `lat` (纬度) 和 `lon` (经度)。
>
> **注意**: 这两个值是整数，可能代表的是将实际浮点数坐标乘以一个倍数（例如 `100000`）后取整的结果。
>
> ```json
> {
>   "position": {
>     "lat": 3123456,  // 示例纬度
>     "lon": 12112345  // 示例经度
>   }
> }
> ```
>
> 在 `GET` 请求中，这两个参数将作为 query string 传递，例如 `?lat=3123456&lon=12112345`。在 `POST` 请求或 WebSocket 消息中，它将作为 JSON body 的一部分。

---

### **一、 核心交互服务 (`xiaozhi-server` - Python)**

这是系统的核心，负责处理实时的语音识别（ASR）、对话和语音合成（TTS）。主要的交互方式是 **WebSocket**。

#### **1.1 WebSocket 接口**

这是与设备���客户端进行实时双向通信的主要方式。

*   **连接地址**: `ws://<your_server_ip>:8000/ws`
*   **通信流程**: 
    1.  客户端与服务器建立 WebSocket 连接。
    2.  **认证**: 连接建立后，客户端必须发送第一条包含 `position` 的认证消息。
    3.  **实时通信**: 认证通过后，客户端可以向服务器发送音频流数据。
    4.  连接关闭。

#### **1.2 数据结构与示例**

**1.2.1 认证消息 (客户端 -> 服务器)**

*   **结构**:
    ```json
    {
      "type": "auth",
      "data": {
        "token": "your_device_token_or_api_key",
        "position": {
          "lat": 3123456,
          "lon": 12112345
        }
      }
    }
    ```
*   **字段说明**:
    *   `token`: 认证令牌。
    *   `position`: 地理位置信息。

**1.2.2 音频数据 (客户端 -> 服务器)**

*   **结构**: 二进制的 PCM 音频数据 (`16bit, 16kHz, 单声道`)。

**1.2.3 控制消息 (客户端 -> 服务器)**

*   **结束对话**:
    ```json
    {
      "type": "control",
      "data": {
        "action": "stop",
        "position": {
          "lat": 3123456,
          "lon": 12112345
        }
      }
    }
    ```

**1.2.4 服务器响应 (服务器 -> 客户端)**

服务器响应消息结构不变。

---

#### **1.3 交互示例代码**

**Python 示例**

```python
import asyncio
import websockets
import json

SERVER_URL = "ws://localhost:8000/ws"
AUTH_TOKEN = "your_secret_token"
USER_POSITION = {"lat": 3123456, "lon": 12112345}

async def audio_interaction():
    async with websockets.connect(SERVER_URL) as websocket:
        # 1. 发送认证消息
        auth_message = {
            "type": "auth",
            "data": {
                "token": AUTH_TOKEN,
                "position": USER_POSITION
            }
        }
        await websocket.send(json.dumps(auth_message))
        print(f"-> Sent Auth: {auth_message}")

        # ... (接收认证响应) ...
        response = await websocket.recv()
        print(f"<- Received: {response}")
        auth_response = json.loads(response)
        if auth_response.get("data", {}).get("status") != "ok":
            print("Authentication failed.")
            return

        # ... (模拟发送音频) ...
        print("-> Simulating sending audio stream...")
        await asyncio.sleep(1)

        # 4. 发送结束指令
        stop_message = {
            "type": "control",
            "data": {
                "action": "stop",
                "position": USER_POSITION
            }
        }
        await websocket.send(json.dumps(stop_message))
        print(f"-> Sent Stop: {stop_message}")

        # ... (接收后续消息) ...
        try:
            while True:
                message = await websocket.recv()
                print(f"<- Received: {message}")
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server.")

if __name__ == "__main__":
    asyncio.run(audio_interaction())
```

**JavaScript 示例 (浏览器环境)**

```javascript
const SERVER_URL = "ws://localhost:8000/ws";
const AUTH_TOKEN = "your_secret_token";
const USER_POSITION = { lat: 3123456, lon: 12112345 };

let socket = null;

function connectWebSocket() {
    socket = new WebSocket(SERVER_URL);

    socket.onopen = function(event) {
        console.log("WebSocket connection established.");
        const authMessage = {
            type: "auth",
            data: {
                token: AUTH_TOKEN,
                position: USER_POSITION
            }
        };
        socket.send(JSON.stringify(authMessage));
        console.log("-> Sent Auth:", authMessage);
    };

    socket.onmessage = function(event) {
        // ... (消息处理逻辑不变) ...
        console.log("<- Received:", event.data);
    };

    socket.onclose = function(event) { console.log("WebSocket closed."); };
    socket.onerror = function(error) { console.error("WebSocket Error:", error); };
}

function stopInteraction() {
    const stopMessage = {
        type: "control",
        data: {
            action: "stop",
            position: USER_POSITION
        }
    };
    socket.send(JSON.stringify(stopMessage));
    console.log("-> Sent Stop:", stopMessage);
}

connectWebSocket();
```

---

#### **1.4 HTTP 接口**

`xiaozhi-server` 的 TTS 接口。

*   **URL**: `POST /api/tts`
*   **请求体 (JSON)**:
    ```json
    {
      "text": "你好，欢迎使用小智语音服务。",
      "voice_name": "default",
      "position": {
        "lat": 3123456,
        "lon": 12112345
      }
    }
    ```
*   **示例 (curl)**:
    ```bash
    curl -X POST http://localhost:8000/api/tts \
         -H "Content-Type: application/json" \
         -d '{"text": "你好", "position": {"lat": 3123456, "lon": 12112345}}' \
         --output test_audio.mp3
    ```

---

### **二、 后台管理服务 (`manager-api` - Java)**

#### **2.1 通用约定**

*   **根路径**: `/prod-api`
*   **认证**: JWT
*   **全局参数**: 所有请求均需携带 `position` 信息。

#### **2.2 关键接口示例**

**2.2.1 用户登录**

*   **URL**: `POST /prod-api/login`
*   **请求体**:
    ```json
    {
      "username": "admin",
      "password": "your_password",
      "position": {
        "lat": 3123456,
        "lon": 12112345
      }
    }
    ```

**2.2.2 获取设备列表**

*   **URL**: `GET /prod-api/manager/device/list`
*   **Query 参数**:
    *   `pageNum`, `pageSize`
    *   `lat`, `lon` (例如: `?pageNum=1&lat=3123456&lon=12112345`)

**2.2.3 添加设备**

*   **URL**: `POST /prod-api/manager/device`
*   **请求体**:
    ```json
    {
      "deviceName": "卧室的小智",
      "remark": "放在卧室床头",
      "position": {
        "lat": 3123456,
        "lon": 12112345
      }
    }
    ```

#### **2.3 交互示例代码 (JavaScript)**

```javascript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8080/prod-api',
  headers: { 'Content-Type': 'application/json' }
});

// ... (拦截器添加 Token 不变) ...

const USER_POSITION = { lat: 3123456, lon: 12112345 };

// 登录
async function login(username, password) {
  const response = await apiClient.post('/login', {
    username,
    password,
    position: USER_POSITION
  });
  // ...
}

// 获取设备列表
async function getDevices(pageNum = 1, pageSize = 10) {
  const response = await apiClient.get('/manager/device/list', {
    params: {
      pageNum,
      pageSize,
      lat: USER_POSITION.lat,
      lon: USER_POSITION.lon
    }
  });
  return response.data;
}

// ...
```