from bot_framework.entities.bot_message import BotMessage
from bot_framework.protocols.i_message_service import IMessageService
from src.chat.actions.send_to_agent_action import SendToAgentAction


class TextMessageHandler:
    allowed_roles: set[str] | None = {"admin"}

    def __init__(
        self,
        send_to_agent_action: SendToAgentAction,
        message_service: IMessageService,
    ) -> None:
        self.send_to_agent_action = send_to_agent_action
        self.message_service = message_service

    def handle(self, message: BotMessage) -> None:
        if not message.from_user:
            raise ValueError("message.from_user is required but was None")

        if not message.text:
            return

        thinking_msg = self.message_service.send(
            chat_id=message.chat_id,
            text="Думаю...",
        )

        self.send_to_agent_action.execute(
            chat_id=message.chat_id,
            user_id=message.from_user.id,
            text=message.text,
            thinking_message_id=thinking_msg.message_id,
        )
