import httpx
import openai
from openai.types import CompletionUsage
from config.logger import setup_logging
from core.utils.util import check_model_key
from core.providers.llm.base import LLMProviderBase
import os
import glob

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config):
        self.model_name = config.get("model_name")
        self.api_key = config.get("api_key")
        if "base_url" in config:
            self.base_url = config.get("base_url")
        else:
            self.base_url = config.get("url")
        # 增加timeout的配置项，单位为秒
        timeout = config.get("timeout", 300)
        self.timeout = int(timeout) if timeout else 300

        param_defaults = {
            "max_tokens": (500, int),
            "temperature": (0.7, lambda x: round(float(x), 1)),
            "top_p": (1.0, lambda x: round(float(x), 1)),
            "frequency_penalty": (0, lambda x: round(float(x), 1)),
        }

        for param, (default, converter) in param_defaults.items():
            value = config.get(param)
            try:
                setattr(
                    self,
                    param,
                    converter(value) if value not in (None, "") else default,
                )
            except (ValueError, TypeError):
                setattr(self, param, default)

        # RAG配置
        self.rag_enabled = config.get("rag_enabled", False)
        self.rag_documents = []
        if self.rag_enabled:
            rag_path = config.get("rag_path")
            if rag_path and os.path.isdir(rag_path):
                self._load_rag_documents(rag_path)
            else:
                logger.bind(tag=TAG).warning(f"RAG已启用，但rag_path '{rag_path}' 不是有效目录。")

        logger.debug(
            f"意图识别参数初始化: {self.temperature}, {self.max_tokens}, {self.top_p}, {self.frequency_penalty}"
        )

        model_key_msg = check_model_key("LLM", self.api_key)
        if model_key_msg:
            logger.bind(tag=TAG).error(model_key_msg)
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=httpx.Timeout(self.timeout))

    def _load_rag_documents(self, path):
        """从指定路径加载所有Markdown文件。"""
        logger.bind(tag=TAG).info(f"从以下路径加载RAG文档: {path}")
        for md_file in glob.glob(os.path.join(path, "*.md")):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    self.rag_documents.append(f.read())
                logger.bind(tag=TAG).info(f"已加载RAG文档: {md_file}")
            except Exception as e:
                logger.bind(tag=TAG).error(f"加载RAG文档 {md_file} 时出错: {e}")
        if not self.rag_documents:
            logger.bind(tag=TAG).warning(f"在RAG路径中未找到Markdown文件: {path}")

    def _get_rag_context(self, query):
        """
        检索RAG上下文。
        目前，它返回所有文档。
        未来可在此实现更复杂的搜索/检索机制。
        """
        if not self.rag_documents:
            return None
        
        # 简单实现：连接所有文档。
        # 在实际场景中，您可以在此处实现某种形式的语义搜索
        # 以查找与给定查询最相关的文档。
        return "\n\n".join(self.rag_documents)

    def response(self, session_id, dialogue, **kwargs):
        if self.rag_enabled:
            # 假设最后一条消息是用户的查询
            if dialogue and dialogue[-1]["role"] == "user":
                user_query = dialogue[-1]["content"]
                rag_context = self._get_rag_context(user_query)
                if rag_context:
                    # 使用RAG上下文增强用户查询
                    augmented_query = f"请根据以下资料回答问题:\n---\n{rag_context}\n---\n问题是: {user_query}"
                    # 创建一个新的对话列表以避免修改原始列表
                    dialogue = dialogue[:-1] + [{"role": "user", "content": augmented_query}]
        try:
            responses = self.client.chat.completions.create(
                model=self.model_name,
                messages=dialogue,
                stream=True,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                top_p=kwargs.get("top_p", self.top_p),
                frequency_penalty=kwargs.get(
                    "frequency_penalty", self.frequency_penalty
                ),
            )

            is_active = True
            for chunk in responses:
                try:
                    # 检查是否存在有效的choice且content不为空
                    delta = (
                        chunk.choices[0].delta
                        if getattr(chunk, "choices", None)
                        else None
                    )
                    content = delta.content if hasattr(delta, "content") else ""
                except IndexError:
                    content = ""
                if content:
                    # 处理标签跨多个chunk的情况
                    if "<think>" in content:
                        is_active = False
                        content = content.split("<think>")[0]
                    if "</think>" in content:
                        is_active = True
                        content = content.split("</think>")[-1]
                    if is_active:
                        yield content

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in response generation: {e}")

    def response_with_functions(self, session_id, dialogue, functions=None):
        if self.rag_enabled:
            if dialogue and dialogue[-1]["role"] == "user":
                user_query = dialogue[-1]["content"]
                rag_context = self._get_rag_context(user_query)
                if rag_context:
                    augmented_query = f"请根据以下资料回答问题或调用合适的工具:\n---\n{rag_context}\n---\n问题是: {user_query}"
                    dialogue = dialogue[:-1] + [{"role": "user", "content": augmented_query}]
        try:
            stream = self.client.chat.completions.create(
                model=self.model_name, messages=dialogue, stream=True, tools=functions
            )

            for chunk in stream:
                # 检查是否存在有效的choice且content不为空
                if getattr(chunk, "choices", None):
                    yield chunk.choices[0].delta.content, chunk.choices[
                        0
                    ].delta.tool_calls
                # 存在 CompletionUsage 消息时，生成 Token 消耗 log
                elif isinstance(getattr(chunk, "usage", None), CompletionUsage):
                    usage_info = getattr(chunk, "usage", None)
                    logger.bind(tag=TAG).info(
                        f"Token 消耗：输入 {getattr(usage_info, 'prompt_tokens', '未知')}，"
                        f"输出 {getattr(usage_info, 'completion_tokens', '未知')}，"
                        f"共计 {getattr(usage_info, 'total_tokens', '未知')}"
                    )

        except Exception as e:
            logger.bind(tag=TAG).error(f"Error in function call streaming: {e}")
            yield f"【OpenAI服务响应异常: {e}】", None
