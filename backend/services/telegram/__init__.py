from schemas.movies import MovieDataOut
from enum import Enum
from services.avbase import get_information_by_work_id_service
from sqlalchemy.orm import Session


class DownloadStatus(str, Enum):
    START_DOWNLOAD = "【开始下载】"
    ADD_SUBSCRIBE = "【添加订阅】"


def _generate_download_information(
    work: MovieDataOut, status: DownloadStatus = DownloadStatus.START_DOWNLOAD
) -> str:
    movie_details = f"*{status.value}*: {work.work_id}\n"
    product = work.primary_product or (work.products[0] if work.products else None)

    if work.title:
        movie_details += f"*标题*: {work.title}\n"
    if product and product.maker:
        movie_details += f"*制造商*: {product.maker}\n"
    if product and product.label:
        movie_details += f"*厂牌*: {product.label}\n"
    if work.min_date:
        movie_details += f"*发布日期*: {work.min_date}\n"
    if work.genres:
        movie_details += f"*标签*: {', '.join(work.genres)}\n"
    if product and product.price:
        movie_details += f"*价格*: {product.price}\n"
    if product and product.volume:
        movie_details += f"*时长*: {product.volume} 分钟\n"
    if work.casts:
        actors = ", ".join(cast["name"] for cast in work.casts if "name" in cast)
        movie_details += f"*演员*: {actors}\n"

    return movie_details


async def send_movie_download_message_by_work_id(
    db: Session, work_id: str, status: DownloadStatus = DownloadStatus.START_DOWNLOAD
):
    from modules.notification.telegram import _telegram_bot

    movie_info = await get_information_by_work_id_service(db, work_id)
    movie_details = _generate_download_information(movie_info, status)

    product = movie_info.primary_product or (
        movie_info.products[0] if movie_info.products else None
    )
    image_url = product.image_url if product else None

    await _telegram_bot.send_message_with_image(
        str(image_url),
        movie_details,
    )
