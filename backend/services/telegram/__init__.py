from modules.metadata.avbase import get_information_by_work_id
from schemas.movies import MovieDataOut
from enum import Enum


class DownloadStatus(str, Enum):
    START_DOWNLOAD = "【开始下载】"
    ADD_SUBSCRIBE = "【添加订阅】"


def generate_download_information(
    work: MovieDataOut, status: DownloadStatus = DownloadStatus.START_DOWNLOAD
) -> str:
    movie_details = f"*{status.value}*: {work.work_id}\n"

    if work.title:
        movie_details += f"*标题*: {work.title}\n"
    if work.products and work.products[0].maker:
        movie_details += f"*制造商*: {work.products[0].maker}\n"
    if work.products and work.products[0].label:
        movie_details += f"*厂牌*: {work.products[0].label}\n"
    if work.min_date:
        movie_details += f"*发布日期*: {work.min_date}\n"
    if work.genres:
        movie_details += f"*标签*: {', '.join(work.genres)}\n"
    if work.products and work.products[0].price:
        movie_details += f"*价格*: {work.products[0].price}\n"
    if work.products and work.products[0].volume:
        movie_details += f"*时长*: {work.products[0].volume} 分钟\n"
    if work.casts:
        actors = ", ".join(cast["name"] for cast in work.casts if "name" in cast)
        movie_details += f"*演员*: {actors}\n"

    return movie_details


async def send_movie_download_message_by_work_id(
    work_id: str, status: DownloadStatus = DownloadStatus.START_DOWNLOAD
):
    from modules.notification.telegram import _telegram_bot

    movie_info = await get_information_by_work_id(work_id)
    movie_details = generate_download_information(movie_info, status)

    image_url = movie_info.products[0].image_url if movie_info.products else None

    await _telegram_bot.send_message_with_image(
        str(image_url),
        movie_details,
    )
