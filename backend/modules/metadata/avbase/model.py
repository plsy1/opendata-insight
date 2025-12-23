
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union

class Talent(BaseModel):
    id: int = 0
    deleted_at: Optional[str] = None


class Actor(BaseModel):
    id: int = 0
    name: str = ""
    order: Optional[int] = None
    image_url: Optional[str] = None
    talent: Optional[Talent] = None
    ruby: Optional[str] = None
    note: Optional[str] = None
    

    @field_validator('image_url', mode='before')
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class Cast(BaseModel):
    actor: Actor = Actor()
    note: Optional[str] = None


class MakerLabelSeries(BaseModel):
    name: str = ""


class ProductItemInfo(BaseModel):
    director: Optional[str] = None
    price: Optional[str] = None
    volume: Optional[str] = None


class Product(BaseModel):
    id: int = 0
    product_id: str = ""
    url: str = ""
    image_url: Optional[str] = None
    title: str = ""
    source: Optional[str] = None
    thumbnail_url: str = ""
    date: Optional[str] = None
    maker: Optional[MakerLabelSeries] = MakerLabelSeries()
    label: Optional[MakerLabelSeries] = MakerLabelSeries()
    series: Optional[MakerLabelSeries] = MakerLabelSeries()
    sample_image_urls: List[dict] = []
    iteminfo: Optional[ProductItemInfo] = ProductItemInfo()
    

    @field_validator('image_url', mode='before')
    def empty_str_to_none(cls, v):
        if v == "":
            return None
        return v


class Genre(BaseModel):
    id: int = 0
    name: str = ""
    canonical_id: Optional[Union[str, int]] = None


class Work(BaseModel):
    id: int = 0
    prefix: str = ""
    work_id: str = ""
    title: str = ""
    min_date: Optional[str] = None
    note: Optional[str] = None
    casts: List[Cast] = []
    actors: List[Actor] = []
    tags: List = []
    genres: List[Genre] = []
    products: List[Product] = []
    
    
class AvbaseEverydayReleaseByPrefix(BaseModel):
    prefixName: str
    works:List[Work] = []


class PageProps(BaseModel):
    work: Work = Work()
    editors: List = []
    comments: List = []
    children: List = []
    parents: List = []
    noindex: bool = False
    _sentryTraceData: Optional[str] = None
    _sentryBaggage: Optional[str] = None


class Props(BaseModel):
    pageProps: PageProps = PageProps()
    __N_SSP: bool = False


class MovieInformation(BaseModel):
    props: Props = Props()
    page: str = ""
    query: dict = {}
    buildId: str = ""
    runtimeConfig: dict = {}
    isFallback: bool = False
    isExperimentalCompile: bool = False
    gssp: bool = False
    scriptLoader: List = []


class SocialMedia(BaseModel):
    platform: str = ""
    username: str = ""
    link: str = ""


class Actress(BaseModel):
    name: str = ""
    birthday: str = ""
    height: str = ""
    bust: str = ""
    waist: str = ""
    hip: str = ""
    cup: str = ""
    hobby: str = ""
    prefectures: str = ""
    blood_type: str = ""
    aliases: List[str] = Field(default_factory=list)
    avatar_url: str = ""
    raw_avatar_url: str = ""
    social_media: List[SocialMedia] = Field(default_factory=list)
    
    

class Movie(BaseModel):
    id: str
    title: str
    full_id: str
    release_date: str
    img_url: str
    actors: List[str]
