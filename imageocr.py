import asyncio
import re
from typing import Callable, Awaitable, Any, Optional

import aiohttp
from pydantic import BaseModel, Field


class Filter:
    class Valves(BaseModel):
        priority: int = Field(default=0, description="用于过滤操作的优先级别。")
        OCR_Base_URL: str = Field(
            default="https://api.openai.com", description="LLm OCR API的基础URL。"
        )
        OCR_API_KEY: str = Field(default="", description="API的API密钥。")
        max_retries: int = Field(default=3, description="HTTP请求的最大重试次数。")
        ocr_prompt: str = Field(
            default="Please only recognize and extract the text or data from this image without interpreting, analyzing, or understanding the content. Do not output any additional information. Simply return the recognized text or data content.",
            description="进行OCR识别的提示词",
        )
        model_name: str = Field(default="gemini-1.5-flash-latest", description="用于OCR图像的模型名称。推荐使用gemini系列")

    def __init__(self):
        self.valves = self.Valves()

    async def _perform_ocr(
        self, image: str, event_emitter: Callable[[Any], Awaitable[None]]
    ) -> str:
        """执行OCR识别的内部方法"""
        await event_emitter(
            {
                "type": "status",
                "data": {
                    "description": "✨正在对图像进行文字识别中，请耐心等待...",
                    "done": False,
                },
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.valves.OCR_API_KEY}",
        }
        ocr_body = {
            "model": self.valves.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": self.valves.ocr_prompt}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.valves.ocr_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": image, "detail": "high"},
                        }
                    ],
                },
            ],
        }
        url = f"{self.valves.OCR_Base_URL}/v1/chat/completions"

        async with aiohttp.ClientSession() as session:
            for attempt in range(self.valves.max_retries):
                try:
                    async with session.post(
                        url, json=ocr_body, headers=headers
                    ) as response:
                        response.raise_for_status()
                        response_data = await response.json()
                        result = response_data["choices"][0]["message"]["content"]

                        await event_emitter(
                            {
                                "type": "status",
                                "data": {
                                    "description": "🎉识别成功，交由模型进行处理...",
                                    "done": True,
                                },
                            }
                        )

                        return result
                except Exception as e:
                    if attempt == self.valves.max_retries - 1:
                        raise RuntimeError(f"OCR识别失败：{e}")

    async def inlet(
        self,
        body: dict,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
    ) -> dict:
        messages = body.get("messages", [])

        # 查找图像
        image_info = self._find_image_in_messages(messages)
        if not image_info:
            return body

        message_index, content_index, image = image_info

        # 如果已经是第二轮及以上对话，直接返回
        if (len(messages) // 2) >= 1:
            del messages[message_index]["content"][content_index]
            body["messages"] = messages
            return body

        try:
            # 执行OCR识别
            result = await self._perform_ocr(image, __event_emitter__)

            # 更新消息内容
            messages[message_index]["content"][content_index]["type"] = "text"
            messages[message_index]["content"][content_index].pop("image_url", None)
            messages[message_index]["content"][content_index]["text"] = result
            body["messages"] = messages
        except Exception as e:
            print(f"OCR识别错误: {e}")
            # 可以根据需要进行错误处理

        return body

    def _find_image_in_messages(self, messages):
        """在消息中查找图像"""
        for m_index, message in enumerate(messages):
            if message["role"] == "user" and isinstance(message.get("content"), list):
                for c_index, content in enumerate(message["content"]):
                    if content["type"] == "image_url":
                        return m_index, c_index, content["image_url"]["url"]
        return None

    async def outlet(
        self,
        body: dict,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[dict] = None,
        __model__: Optional[dict] = None,
    ) -> dict:
        return body
