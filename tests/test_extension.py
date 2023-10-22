import pytest
from nonebug import App
from nonebot import get_adapter
from arclet.alconna import Alconna, Args
from nonebot.adapters.onebot.v11 import Bot, Adapter, Message

from tests.fake import fake_group_message_event_v11


@pytest.mark.asyncio()
async def test_extension(app: App):
    from nonebot_plugin_alconna import Extension, on_alconna

    class DemoExtension(Extension):
        @property
        def priority(self) -> int:
            return 1

        @property
        def id(self) -> str:
            return "demo"

        async def catch(self, state, name, annotation, default, **kwargs):
            if annotation is str:
                return {
                    "hello": "Hello!",
                    "world": "World!",
                }.get(name, name)

    add = on_alconna(
        Alconna(
            "add", Args["a", float]["b", float]
        ),
        extensions=[DemoExtension]
    )

    @add.handle()
    async def h(a: float, b: float, hello: str, world: str, test: str):
        """加法测试"""
        await add.send(f"{a} + {b} = {a + b}\n{hello} {world} {test}!")

    async with app.test_matcher(add) as ctx:  # type: ignore
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter)
        event = fake_group_message_event_v11(message=Message("add 1.3 2.4"), user_id=123)
        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "1.3 + 2.4 = 3.7\nHello! World! test!")
