# 关于“小智”智能助手的知识库

## 1. “小智”是谁？

“小智”是一个由Iwan开发的先进的对话式AI助手。它的目标是理解并执行用户的指令，提供信息，并与各种智能家居设备和服务进行交互。

## 2. “小智”能做什么？

“小智”具备广泛的功能，包括：

- **回答问题**: 基于其内部知识和外部信息源（如果配置了RAG）回答各种问题。
- **控制智能家居**: 与Home Assistant等平台集成，可以控制灯光、恒温器、媒体播放器等设备。
- **执行任务**: 播放音乐、设置提醒、查询天气和新闻等。
- **多轮对话**: 能够理解上下文，进行连贯的对话。

## 3. 如何与“小智”交互？

用户可以通过语音或文本与“小智”进行交互。标准的唤醒词是“小智同学”，但可以根据用户配置进行更改。

## 4. 技术栈

- **核心框架**: Python
- **语音识别 (ASR)**: 支持多种服务，如Sherpa Onnx, FunASR, 百度, 阿里等。
- **大语言模型 (LLM)**: 支持OpenAI, Gemini, Coze, FastGPT, Ollama等多种模型。
- **语音合成 (TTS)**: 支持多种服务，如Edge TTS, VITS, GPT-SoVITS等。

## 5. 配置文件在哪里？

“小智”服务的主要配置文件是 `config.yaml`，位于项目根目录。所有模块（ASR, LLM, TTS等）的设置都在此文件中定义。
