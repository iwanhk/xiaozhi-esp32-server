# 小智 ESP32 服务端接口文档

本文档分为两部分：
1.  **WebSocket 通信接口**：用于客户端（ESP32设备、Web测试页面等）与核心服务 (`xiaozhi-server`) 之间的实时语音和文本交互。
2.  **HTTP RESTful API 接口**：用于管理前端 (`manager-web`) 与管理后端 (`manager-api`) 之间的配置和数据管理。

---

## 第一部分：WebSocket 实时通信接口

此接口负责处理实时的双向通信，是 AI 对话功能的核心。

*   **连接地址**: `ws://<your_server_ip>:8080/ws` (具体端口取决于 `config.yaml` 配置)
*   **数据格式**: JSON (除音频流本身为二进制)

### 1. 通用消息结构

所有 JSON 消息都遵循以下基本格式：

```json
{
  "type": "消息类型 (string)",
  "data": {
    // 消息的具体数据 (object)
  }
}
```

---

### 2. 客户端 -> 服务端 消息

#### **2.1 `auth` - 连接认证**
*   **方向**: 客户端 -> 服务端
*   **时机**: WebSocket 连接建立后，发送的第一条消息。
*   **说明**: 用于验证客户端身份。
*   **`data` 结构**:
    ```json
    {
      "token": "your_auth_token"
    }
    ```

#### **2.2 `start` - 开始语音对话**
*   **方向**: 客户端 -> 服务端
*   **时机**: 用户按下录音按钮，准备发送语音流之前。
*   **说明**: 初始化一次语音对话，并传递必要的元数据，包括**位置信息**。
*   **`data` 结构**:
    ```json
    {
      "sample_rate": 16000,       // (int) 音频采样率, e.g., 16000
      "sample_bits": 16,          // (int) 采样位深, e.g., 16
      "channels": 1,              // (int) 声道数, e.g., 1
      "language": "zh_cn",        // (string) 语言, e.g., "zh_cn"
      "audio_format": "pcm",      // (string) 音频格式, e.g., "pcm"
      "position": {               // (object) 用户当前的位置信息
        "x": 100,                 // (int) X 坐标
        "y": 250                  // (int) Y 坐标
      }
    }
    ```

#### **2.3 `text_message` - 发送文本消息**
*   **方向**: 客户端 -> 服务端
*   **时机**: 用户通过输入框发送纯文本消息时。
*   **说明**: 用于非语音的文本对话场景，同时传递**位置信息**。
*   **`data` 结构**:
    ```json
    {
      "text": "帮我查一下今天的天气。", // (string) 用户输入的文本
      "position": {                  // (object) 用户当前的位��信息
        "x": 120,                    // (int) X 坐标
        "y": 280                     // (int) Y 坐标
      }
    }
    ```

#### **2.4 音频二进制流 (Binary Data)**
*   **方向**: 客户端 -> 服务端
*   **时机**: 发送 `start` 消息之后，`end` 消息之前。
*   **说明**: 原始的、连续的音频数据流。**此消息不是 JSON 格式**。

#### **2.5 `end` - 结束语音对话**
*   **方向**: 客户端 -> 服务端
*   **时机**: 用户松开录音按钮，语音流发送完毕。
*   **说明**: 通知服务器当前对话的语音部分已结束。
*   **`data` <strong>结构</strong>**:
    ```json
    {}
    ```

#### **2.6 `ping` - 心跳检测**
*   **方向**: 客户端 -> 服务端
*   **时机**: 定期发送（例如每30秒）。
*   **说明**: 用于保持 WebSocket 连接活跃。
*   **`data` 结构**:
    ```json
    {}
    ```

---

### 3. 服务端 -> 客户端 消息

#### **3.1 `auth_response` - 认证响应**
*   **方向**: 服务端 -> 客户端
*   **说明**: 回复客户端的 `auth` 请求。
*   **`data` 结构**:
    ```json
    {
      "success": true,
      "message": "认证成功"
    }
    ```

#### **3.2 `interim_result` - 实时识别结果**
*   **方向**: 服务端 -> 客户端
*   **说明**: 在用户说话过程中，实时返回的中间 ASR (语音识别) 结果。
*   **`data` 结构**:
    ```json
    {
      "text": "这是中间识别的"
    }
    ```

#### **3.3 `final_result` - 最终识别结果**
*   **方向**: 服务端 -> 客户端
*   **说明**: 用户结束说话后，返回的最终 ASR 结果。
*   **`data` 结构**:
    ```json
    {
      "text": "这是最终识别的完整文本。"
    }
    ```

#### **3.4 `answer` - AI 回答**
*   **方向**: 服务端 -> 客户端
*   **说明**: 服务器在处理完用户意图后，返回的最终答案，可能包含文本和待播放的音频。
*   **`data` 结构**:
    ```json
    {
      "text": "这是AI的回答文本。",                                // (string) 回答的文本内容
      "url": "http://<server_ip>/tts/audio.mp3",             // (string) TTS 合成的语音文件URL (可选)
      "is_final": true,                                      // (boolean) 是否是最终回答
      "intent": "chat",                                      // (string) 意图类型, e.g., "chat", "music"
      "tts_type": "local"                                    // (string) TTS 服务类型, e.g., "local", "ali"
    }
    ```

#### **3.5 `error` - 错误通知**
*   **方向**: 服务端 -> 客户端
*   **说明**: 在处理过程中发生任何错误时，通知客户端。
*   **`data` 结构**:
    ```json
    {
      "message": "这里是具体的错误描述"
    }
    ```

#### **3.6 `pong` - 心跳响应**
*   **方向**: 服务端 -> 客户端
*   **说明**: 回复客户端的 `ping` 请求。
*   **`data` 结构**:
    ```json
    {}
    ```

---

## 第二部分：HTTP RESTful API 接口 (管理后台)

此接口用于管理后台的各种配置项，采用标准的 RESTful 风格。

*   **根路径**: `/api` (取决于 `manager-api` 的配置)
*   **认证方式**: 通常在请求的 Header 中携带 `Authorization: Bearer <jwt_token>`。

### 1. 用户认证 (`/user`)

*   **功能**: 登录
*   **路径**: `/user/login`
*   **方法**: `POST`
*   **请求体**:
    ```json
    {
      "username": "admin",
      "password": "your_password"
    }
    ```
*   **响应**:
    ```json
    {
      "code": 200,
      "msg": "登录成功",
      "data": {
        "token": "generated_jwt_token"
      }
    }
    ```

### 2. 设备管理 (`/device`)

*   **功能**: 获取设备列表 (分页)
*   **路径**: `/device/list`
*   **方法**: `GET`
*   **查询参数**: `pageNum=1&pageSize=10&deviceName=my_device` (deviceName可选)
*   **响应**:
    ```json
    {
      "code": 200,
      "data": {
        "total": 1,
        "list": [
          { "id": 1, "deviceName": "客厅小智", "token": "token_abc", "status": "online" }
        ]
      }
    }
    ```

*   **功能**: 新增设备
*   **路径**: `/device`
*   **方法**: `POST`
*   **请求体**:
    ```json
    {
      "deviceName": "卧室小智",
      "description": "放在卧室的设备"
    }
    ```

*   **功能**: 更新设备
*   **路径**: `/device`
*   **方法**: `PUT`
*   **请求体**:
    ```json
    {
      "id": 2,
      "deviceName": "卧室小智-改",
      "description": "更新后的描述"
    }
    ```

*   **功能**: 删除设备
*   **路径**: `/device/{id}`
*   **方法**: `DELETE`
*   **路径参数**: `id` (设备ID)

### 3. AI 模型管理 (`/model`)

*   **功能**: 获取模型列表
*   **路径**: `/model/list`
*   **方法**: `GET`
*   **查询参数**: `pageNum=1&pageSize=10`

*   **功能**: 新增模型配置
*   **路径**: `/model`
*   **方法**: `POST`
*   **请求体**:
    ```json
    {
      "modelName": "Qwen-7B-Chat",
      "modelType": "LLM",
      "baseUrl": "http://127.0.0.1:8000/v1",
      "apiKey": "your_api_key"
    }
    ```

*   **功能**: 更新模型配置
*   **路径**: `/model`
*   **方法**: `PUT`

*   **功能**: 删除模型配置
*   **路径**: `/model/{id}`
*   **方法**: `DELETE`

### 4. 系统管理 (`/system`)

*   **功能**: 获取系统参数
*   **路径**: `/system/config/list`
*   **方法**: `GET`

*   **功能**: 获取服务状态
*   **路径**: `/system/server/status`
*   **方法**: `GET`
