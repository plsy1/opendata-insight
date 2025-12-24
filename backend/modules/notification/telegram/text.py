from modules.metadata.avbase.model import Actress, MovieDataOut


def actressInformation(name, actress_info: Actress):
    actress_details = f"*【添加订阅】*: {name}\n"

    if actress_info.birthday:
        actress_details += f"**出生日期**: {actress_info.birthday}\n"
    if actress_info.prefectures:
        actress_details += f"**出生地**: {actress_info.prefectures}\n"
    if actress_info.height:
        actress_details += f"**身高**: {actress_info.height}\n"
    if actress_info.hobby:
        actress_details += f"**兴趣爱好**: {actress_info.hobby}\n"
    if actress_info.blood_type:
        actress_details += f"**血型**: {actress_info.blood_type}\n"
    if actress_info.aliases:
        aliases = ", ".join(actress_info.aliases)
        actress_details += f"**别名**: {aliases}\n"
    return actress_details


def movieInformation(keyword: str, work: MovieDataOut) -> str:

    movie_details = f"*【添加订阅】*: {keyword}\n"

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
        movie_details += f"*时长*: {work.products[0].volume}\n"

    if work.casts:
        actors = ", ".join(cast["name"] for cast in work.casts if "name" in cast)
        movie_details += f"*演员*: {actors}\n"

    return movie_details


def DownloadInformation(keyword: str, work: MovieDataOut) -> str:

    movie_details = f"*【添加订阅】*: {keyword}\n"

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
