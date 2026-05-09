"""
通用大模型客户端
支持多种大模型服务：Coze SDK、OpenAI、阿里百炼等
基于 LangChain 生态组件实现
"""
import os
import json
import logging
from typing import Optional, List, Dict, Any, Union, Literal
from dataclasses import dataclass

from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

# Coze SDK
try:
    from coze_coding_dev_sdk import LLMClient as CozeLLMClient
    from coze_coding_utils.runtime_ctx.context import Context, new_context
    COZE_SDK_AVAILABLE = True
except ImportError:
    COZE_SDK_AVAILABLE = False
    CozeLLMClient = None
    Context = None
    new_context = None

# OpenAI
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    ChatOpenAI = None

# 阿里百炼（通义千问）
try:
    from langchain_community.chat_models import TongyiChatLLM
    from langchain_community.llms import Tongyi
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    TongyiChatLLM = None
    Tongyi = None

# DeepSeek
try:
    from langchain_deepseek import ChatDeepSeek
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    ChatDeepSeek = None

# Kimi
try:
    from langchain_aichat import ChatAIChat
    KIMI_AVAILABLE = True
except ImportError:
    KIMI_AVAILABLE = False
    ChatAIChat = None

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """大模型配置"""
    model_type: str = "coze"  # coze, openai, dashscope, deepseek, kimi
    model_name: str = ""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 0.9
    thinking: str = "disabled"
    extra_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


class UniversalLLMClient:
    """
    通用大模型客户端

    支持的大模型类型：
    - coze: Coze 平台大模型（豆包、DeepSeek、Kimi 等）
    - openai: OpenAI GPT 系列
    - dashscope: 阿里百炼（通义千问）
    - deepseek: DeepSeek 大模型
    - kimi: Kimi 大模型
    """

    SUPPORTED_TYPES = ["coze", "openai", "dashscope", "deepseek", "kimi"]

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client: Optional[Runnable] = None
        self._initialize_client()

    def _initialize_client(self):
        """根据配置初始化对应的客户端"""
        model_type = self.config.model_type.lower()

        if model_type == "coze":
            self._init_coze_client()
        elif model_type == "openai":
            self._init_openai_client()
        elif model_type == "dashscope":
            self._init_dashscope_client()
        elif model_type == "deepseek":
            self._init_deepseek_client()
        elif model_type == "kimi":
            self._init_kimi_client()
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

    def _init_coze_client(self):
        """初始化 Coze SDK 客户端"""
        if not COZE_SDK_AVAILABLE:
            raise ImportError("Coze SDK 未安装，请运行: pip install coze-coding-dev-sdk")

        ctx = new_context(method="llm_invoke") if new_context else None
        self._client = CozeLLMClient(ctx=ctx)

    def _init_openai_client(self):
        """初始化 OpenAI 客户端"""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI 包未安装，请运行: pip install langchain-openai")

        params = {
            "model": self.config.model_name or "gpt-4",
            "temperature": self.config.temperature,
        }

        if self.config.api_key:
            params["api_key"] = self.config.api_key
        elif os.getenv("OPENAI_API_KEY"):
            params["api_key"] = os.getenv("OPENAI_API_KEY")

        if self.config.base_url:
            params["base_url"] = self.config.base_url

        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens

        params.update(self.config.extra_params)
        self._client = ChatOpenAI(**params)

    def _init_dashscope_client(self):
        """初始化阿里百炼（通义千问）客户端"""
        if not DASHSCOPE_AVAILABLE:
            raise ImportError("阿里百炼包未安装，请运行: pip install dashscope 或请联系管理员")

        api_key = self.config.api_key or os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("阿里百炼需要设置 DASHSCOPE_API_KEY 环境变量或传入 api_key")

        # 通义千问模型映射
        model_name = self.config.model_name or "qwen-plus"

        params = {
            "model": model_name,
            "dashscope_api_key": api_key,
            "temperature": self.config.temperature,
        }

        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens

        params.update(self.config.extra_params)

        try:
            # 尝试使用 langchain_community 的 Tongyi
            self._client = TongyiChatLLM(**params)
        except Exception:
            # 如果失败，抛出明确的错误
            raise ImportError(
                "阿里百炼配置失败，请确保已安装 dashscope 包并配置正确的 API Key\n"
                "pip install dashscope"
            )

    def _init_deepseek_client(self):
        """初始化 DeepSeek 客户端"""
        if not DEEPSEEK_AVAILABLE:
            raise ImportError("DeepSeek 包未安装，请运行: pip install langchain-deepseek")

        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek 需要设置 DEEPSEEK_API_KEY 环境变量或传入 api_key")

        params = {
            "model": self.config.model_name or "deepseek-chat",
            "deepseek_api_key": api_key,
            "temperature": self.config.temperature,
        }

        if self.config.base_url:
            params["base_url"] = self.config.base_url

        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens

        params.update(self.config.extra_params)
        self._client = ChatDeepSeek(**params)

    def _init_kimi_client(self):
        """初始化 Kimi 客户端"""
        if not KIMI_AVAILABLE:
            raise ImportError("Kimi 包未安装，请运行: pip install langchain-aichat")

        api_key = self.config.api_key or os.getenv("KIMI_API_KEY")
        if not api_key:
            raise ValueError("Kimi 需要设置 KIMI_API_KEY 环境变量或传入 api_key")

        params = {
            "model": self.config.model_name or "moonshot-v1-8k",
            "kimi_api_key": api_key,
            "temperature": self.config.temperature,
        }

        if self.config.base_url:
            params["base_url"] = self.config.base_url

        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens

        params.update(self.config.extra_params)
        self._client = ChatAIChat(**params)

    def invoke(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseMessage:
        """
        调用大模型

        Args:
            messages: 消息列表
            model: 模型名称（可选，会覆盖配置）
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            AI 响应消息
        """
        model_type = self.config.model_type.lower()

        # Coze SDK 使用不同的调用方式
        if model_type == "coze":
            return self._invoke_coze(messages, model, temperature, max_tokens, **kwargs)

        # 其他模型使用 LangChain 标准方式
        return self._invoke_langchain(messages, model, temperature, max_tokens, **kwargs)

    def _invoke_coze(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseMessage:
        """Coze SDK 调用方式"""
        invoke_params = {
            "messages": messages,
            "model": model or self.config.model_name,
        }

        if temperature is not None:
            invoke_params["temperature"] = temperature
        elif self.config.temperature:
            invoke_params["temperature"] = self.config.temperature

        if max_tokens is not None:
            invoke_params["max_completion_tokens"] = max_tokens
        elif self.config.max_tokens:
            invoke_params["max_completion_tokens"] = self.config.max_tokens

        if self.config.thinking and self.config.thinking != "disabled":
            invoke_params["thinking"] = self.config.thinking

        invoke_params.update(kwargs)

        return self._client.invoke(**invoke_params)

    def _invoke_langchain(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> BaseMessage:
        """LangChain 通用调用方式"""
        # 如果指定了模型，可能需要重新初始化
        if model and model != self.config.model_name:
            original_model = self.config.model_name
            self.config.model_name = model
            try:
                self._client.model_name = model
            except AttributeError:
                # 如果客户端不支持动态修改，重新初始化
                self._initialize_client()
            finally:
                self.config.model_name = original_model

        invoke_params = {"messages": messages}

        if temperature is not None:
            invoke_params["temperature"] = temperature

        if max_tokens is not None:
            invoke_params["max_tokens"] = max_tokens

        invoke_params.update(kwargs)

        return self._client.invoke(**invoke_params)

    def stream(
        self,
        messages: List[BaseMessage],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ):
        """
        流式调用大模型

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            **kwargs: 其他参数

        Yields:
            响应片段
        """
        model_type = self.config.model_type.lower()

        if model_type == "coze":
            for chunk in self._invoke_coze(messages, model, temperature, **kwargs):
                yield chunk
        else:
            for chunk in self._client.stream(messages=messages, temperature=temperature, **kwargs):
                yield chunk


class LLMClientFactory:
    """大模型客户端工厂"""

    @staticmethod
    def from_config_file(config_path: str) -> UniversalLLMClient:
        """
        从配置文件创建客户端

        Args:
            config_path: 配置文件路径（JSON 格式）

        Returns:
            通用大模型客户端实例
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        llm_config_data = config_data.get("config", {})

        # 提取模型类型
        model_type = llm_config_data.get("model_type", "coze")
        model_name = llm_config_data.get("model", "")
        api_key = llm_config_data.get("api_key")
        base_url = llm_config_data.get("base_url")
        temperature = llm_config_data.get("temperature", 0.7)
        max_tokens = llm_config_data.get("max_completion_tokens") or llm_config_data.get("max_tokens")
        top_p = llm_config_data.get("top_p", 0.9)
        thinking = llm_config_data.get("thinking", "disabled")
        extra_params = llm_config_data.get("extra_params", {})

        config = LLMConfig(
            model_type=model_type,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            thinking=thinking,
            extra_params=extra_params
        )

        return UniversalLLMClient(config)

    @staticmethod
    def create(
        model_type: str,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> UniversalLLMClient:
        """
        直接创建客户端

        Args:
            model_type: 模型类型 (coze, openai, dashscope, deepseek, kimi)
            model_name: 模型名称
            api_key: API Key
            base_url: API 基础 URL
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            通用大模型客户端实例
        """
        config = LLMConfig(
            model_type=model_type,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_params=kwargs
        )

        return UniversalLLMClient(config)


def get_available_model_types() -> List[str]:
    """获取当前环境支持的模型类型"""
    available = []

    if COZE_SDK_AVAILABLE:
        available.append("coze")

    if OPENAI_AVAILABLE:
        available.append("openai")

    if DASHSCOPE_AVAILABLE:
        available.append("dashscope")

    if DEEPSEEK_AVAILABLE:
        available.append("deepseek")

    if KIMI_AVAILABLE:
        available.append("kimi")

    return available
