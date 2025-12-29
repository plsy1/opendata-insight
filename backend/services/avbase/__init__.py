from modules.metadata.avbase import (
    MoviePoster,
    parse_movie_lists,
    parse_actor_information,
    parse_avbase_index_actor,
)
from schemas.actor import ActorDataOut, AvbaseIndexActorOut
from sqlalchemy.orm import Session
from database import ActorData, avbaseNewbie, avbasePopular


async def get_movie_list_by_actor_name_service(
    name: str, page: int
) -> list[MoviePoster]:
    url = f"https://www.avbase.net/talents/{name}?q=&page={page}"
    return await parse_movie_lists(url)


async def get_movie_list_by_keywords_service(
    keywords: str, page: int
) -> list[MoviePoster]:
    url = f"https://www.avbase.net/works?q={keywords}&page={page}"
    return await parse_movie_lists(url)


async def get_actor_information_by_name_service(db: Session, name: str) -> ActorDataOut:

    records = db.query(ActorData).where(ActorData.name == name).first()

    if not records:
        url = f"https://www.avbase.net/talents/{name}"
        data = await parse_actor_information(url)
        new_actor = ActorData(**data.model_dump())
        db.add(new_actor)
        db.commit()
        db.refresh(new_actor)

        records = new_actor

    return ActorDataOut.model_validate(records)


async def get_avbase_index_actor_service(db: Session):
    newbie_records = db.query(avbaseNewbie).all()
    popular_records = db.query(avbasePopular).all()

    if not newbie_records or not popular_records:
        newbie_data_list, popular_data_list = await parse_avbase_index_actor()

        newbie_records = [
            avbaseNewbie(name=a.name, avatar_url=a.avatar_url) for a in newbie_data_list
        ]
        popular_records = [
            avbasePopular(name=a.name, avatar_url=a.avatar_url)
            for a in popular_data_list
        ]

        db.add_all(newbie_records)
        db.add_all(popular_records)
        db.commit()

        for record in newbie_records + popular_records:
            db.refresh(record)

    result = {
        "newbie_talents": [
            AvbaseIndexActorOut.model_validate(r) for r in newbie_records
        ],
        "popular_talents": [
            AvbaseIndexActorOut.model_validate(r) for r in popular_records
        ],
    }

    return result
