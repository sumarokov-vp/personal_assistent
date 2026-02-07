from anyio.from_thread import BlockingPortal, start_blocking_portal
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
)


class AgentClient:
    def __init__(self) -> None:
        self._clients: dict[int, ClaudeSDKClient] = {}
        self._portal: BlockingPortal = start_blocking_portal().__enter__()

    def _get_or_create_client(self, user_id: int) -> ClaudeSDKClient:
        if user_id not in self._clients:
            options = ClaudeAgentOptions(
                cwd="/home/sumarokov",
                permission_mode="bypassPermissions",
            )
            self._clients[user_id] = ClaudeSDKClient(options)
        return self._clients[user_id]

    def send_message(self, user_id: int, text: str) -> str:
        return self._portal.call(self._send_message_async, user_id, text)

    async def _send_message_async(self, user_id: int, text: str) -> str:
        client = self._get_or_create_client(user_id)

        if client._transport is None:
            await client.connect()

        await client.query(text)

        response_parts: list[str] = []
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)
            elif isinstance(message, ResultMessage) and message.is_error:
                await self._reset_client(user_id)
                raise RuntimeError(f"Claude SDK error: {message.result}")

        return "\n".join(response_parts)

    async def _reset_client(self, user_id: int) -> None:
        if user_id in self._clients:
            await self._clients[user_id].disconnect()
            del self._clients[user_id]
