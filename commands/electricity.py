from ..utils import check_query_limit, query_electricity
from ..data_manager import data_manager
from ..csust_api import building_data

from nonebot import on_command, require
from nonebot.rule import to_me
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import (
    Event,
    Message,
    GroupMessageEvent,
    PrivateMessageEvent,
    MessageSegment,
)

require("nonebot_plugin_txt2img")
from nonebot_plugin_txt2img import Txt2Img

electricity = on_command(
    "电量", aliases={"电量查询", "查电量", "查询电量"}, rule=to_me()
)


@electricity.handle()
async def handle_electricity(event: Event, args: Message = CommandArg()):
    if isinstance(event, PrivateMessageEvent):
        user_id = f"user-{event.get_user_id()}"
    elif isinstance(event, GroupMessageEvent):
        user_id = f"group-{event.group_id}"

    args_text = args.extract_plain_text().strip()

    # 检查查询次数限制
    if isinstance(event, GroupMessageEvent) and args_text:
        # 处理用户提供参数查询电量
        query_limit_identifier = f"user-{event.get_user_id()}"
    else:
        # 处理普通绑定查询电量
        query_limit_identifier = user_id

    if not check_query_limit(query_limit_identifier):
        await electricity.finish("查询次数已达上限，每小时最多查询两次。请稍后再试")

    # 检查用户是否提供了查询参数
    if not args_text:
        if user_id in data_manager.binding_data:
            campus, building_name, room_id = data_manager.binding_data[user_id]
            await query_electricity(
                campus, building_name, room_id, electricity, query_limit_identifier
            )
        else:
            await electricity.finish(
                "未检测到绑定信息，请先绑定宿舍，或直接使用命令指定宿舍"
            )
    else:
        parts = args_text.split()
        if len(parts) == 1:
            campus = parts[0]
            if campus in building_data:
                buildings = "\n".join(building_data[campus].keys())
                pic = Txt2Img().draw(f"{campus}的宿舍楼列表", buildings)
                await electricity.finish(MessageSegment.image(pic))
            else:
                await electricity.finish(
                    "校区名称错误，请输入有效的校区（如：云塘、金盆岭）"
                )
        elif len(parts) == 3:
            campus, building_name, room_id = parts
            await query_electricity(
                campus, building_name, room_id, electricity, query_limit_identifier
            )
        else:
            await electricity.finish(
                "请输入正确的格式：\n1. 查询校区宿舍楼：电量 云塘\n2. 查询电量：电量 云塘 16栋A区 A101"
            )
