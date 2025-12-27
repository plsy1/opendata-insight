from enum import Enum

class Operation(str, Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    COLLECT = "collect"
    UNCOLLECT = "uncollect"

class MovieStatus(str, Enum):
    SUBSCRIBE = "subscribe"
    DOWNLOADED = "downloaded"

class ActorListType(str, Enum):
    SUBSCRIBE = "subscribe"
    COLLECT = "collect"

class MovieFeedOperation(Enum):
    ADD = "add"                 
    REMOVE = "remove"           
    MARK_DOWNLOADED = "done"    