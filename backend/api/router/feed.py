from fastapi import APIRouter, HTTPException, Response, Depends, Form
from core.auth import *
from sqlalchemy.orm import Session
from core.database import RSSItem, RSSFeed, ActressCollect, get_db
from modules.notification.telegram.text import *
from modules.metadata.avbase import *
from core.config import _config
from core.system import replace_domain_in_value
from services.feed import *

router = APIRouter()


@router.post("/addKeywords")
async def add_feed(
    actors: str = Form(...),
    keyword: str = Form(...),
    img: str = Form(None),
    link: str = Form(None),
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):

    r = await add_movie_feed(actors, keyword, img, link, db)

    if r:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.delete("/delKeywords")
async def remove_feed(
    keyword: str = Form(...),
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):
    r = await remove_movie_feed(keyword, db)

    if r:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/addFeeds")
async def add_rss_feed(
    avatar_img_url: str = Form(...),
    actor_name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):
    import urllib.parse

    actor_name = urllib.parse.unquote(actor_name)

    r = await add_performer_feed(actor_name, db)

    if r:
        return Response(status_code=status.HTTP_200_OK)
    else:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)


@router.post("/addActressCollect")
async def add_actress_collect(
    avatar_url: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):

    existing_feed = (
        db.query(ActressCollect).filter(ActressCollect.avatar_url == avatar_url).first()
    )
    if existing_feed:
        raise HTTPException(status_code=400, detail="actress collect already exists.")

    new_collect = ActressCollect(avatar_url=avatar_url, name=name)

    try:
        db.add(new_collect)
        db.commit()
        db.refresh(new_collect)

        return {
            "message": f"Successfully added Actress to Collect: {name}",
            "feed_id": new_collect.id,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error adding RSS feed: {str(e)}")


@router.delete("/delFeeds")
async def remove_rss_feed(
    title: str = Form(...),
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):
    existing_feed = db.query(RSSFeed).filter(RSSFeed.title == title).first()

    if not existing_feed:
        raise HTTPException(status_code=404, detail="RSS feed not found.")

    try:
        db.delete(existing_feed)
        db.commit()
        return {"message": f"Successfully removed RSS feed: {existing_feed.title}"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error removing RSS feed: {str(e)}"
        )


@router.delete("/delActressCollect")
async def remove_actress_collect(
    name: str = Form(...),
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):
    existing_feed = db.query(ActressCollect).filter(ActressCollect.name == name).first()

    if not existing_feed:
        raise HTTPException(status_code=404, detail="Actress not found.")

    try:
        db.delete(existing_feed)
        db.commit()
        return {
            "message": f"Successfully removed Actress from Collect: {existing_feed.name}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Error removing Actress from Collect: {str(e)}"
        )


@router.get("/getKeywordsFeedList")
async def get_keywords_feed_list(
    db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        feeds = (
            db.query(RSSItem)
            .filter(RSSItem.downloaded == False)
            .order_by(RSSItem.id.desc())
            .all()
        )
        feeds_dicts = [
            {k: v for k, v in feed.__dict__.items() if k != "_sa_instance_state"}
            for feed in feeds
        ]
        feeds_dicts = replace_domain_in_value(
            feeds_dicts, _config.get("SYSTEM_IMAGE_PREFIX")
        )
        return feeds_dicts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feeds: {str(e)}")


@router.get("/getDownloadedKeywordsFeedList")
async def get_downloaded_keywords_feed_list(
    db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        feeds = (
            db.query(RSSItem)
            .filter(RSSItem.downloaded == True)
            .order_by(RSSItem.id.desc())
            .all()
        )
        feeds_dicts = [
            {k: v for k, v in feed.__dict__.items() if k != "_sa_instance_state"}
            for feed in feeds
        ]
        feeds_dicts = replace_domain_in_value(
            feeds_dicts, _config.get("SYSTEM_IMAGE_PREFIX")
        )
        return feeds_dicts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feeds: {str(e)}")


@router.get("/getFeedsList")
async def get_feed_list(
    db: Session = Depends(get_db), isValid: str = Depends(tokenInterceptor)
):
    try:
        feeds = db.query(RSSFeed).all()
        feeds_dicts = [
            {k: v for k, v in feed.__dict__.items() if k != "_sa_instance_state"}
            for feed in feeds
        ]
        feeds_dicts = replace_domain_in_value(
            feeds_dicts, _config.get("SYSTEM_IMAGE_PREFIX")
        )
        return feeds_dicts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feeds: {str(e)}")


@router.get("/getCollectList")
async def get_collect_list(
    db: Session = Depends(get_db),
    isValid: str = Depends(tokenInterceptor),
):
    try:
        feeds = db.query(ActressCollect).all()

        feeds_dicts = [
            {k: v for k, v in feed.__dict__.items() if k != "_sa_instance_state"}
            for feed in feeds
        ]
        feeds_dicts = replace_domain_in_value(
            feeds_dicts, _config.get("SYSTEM_IMAGE_PREFIX")
        )
        return feeds_dicts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving feeds: {str(e)}")
