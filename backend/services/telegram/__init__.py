from modules.notification.telegram import _telegram_bot
from modules.metadata.avbase import get_information_by_work_id
from schemas.movies import MovieDataOut


def generate_download_information(work: MovieDataOut) -> str:

    movie_details = f"*开始下载】*: {work.work_id}\n"

    if work.title:
        movie_details += f"*标题*: {work.title}\n"
    if work.products and work.products[0].maker and work.products[0].maker:
        movie_details += f"*制造商*: {work.products[0].maker}\n"
    if work.products[0].label:
        movie_details += f"*厂牌*: {work.products[0].label}\n"
    if work.min_date:
        movie_details += f"*发布日期*: {work.min_date}\n"
    if work.genres:
        movie_details += f"*标签*: {work.genres}\n"
    if work.products and work.products[0].price:
        movie_details += f"*价格*: {work.products[0].price}\n"
    if work.products and work.products[0] and work.products[0].volume:
        movie_details += f"*时长*: {work.products[0].volume} 分钟\n"

    if work.casts:
        actors = ", ".join(cast["name"] for cast in work.casts if "name" in cast)
        movie_details += f"*演员*: {actors}\n"

    return movie_details


async def send_movie_download_message_by_work_id(work_id: str):
    movie_info = await get_information_by_work_id(work_id)
    movie_details = generate_download_information(movie_info)

    await _telegram_bot.send_message_with_image(
        str(movie_info.products.image_url),
        movie_details,
    )
