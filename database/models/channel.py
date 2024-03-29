from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, VARCHAR, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    channel_id = Column(VARCHAR, unique=True)
    # NB: Channel title can only be acquired when a video belonging to this Channel shows up,
    #     as it isn't included in the subscribe GET request that init this object.
    channel_title = Column(VARCHAR)
    videos = relationship("Video", back_populates='channel')
    # DB entry creation date.
    added_on = Column(DateTime)
    # DB entry last modified date.
    last_modified = Column(DateTime)
    subscribed = Column(Boolean)
    expires_on = Column(DateTime)

    def __init__(self, channel_id, channel_title=None, added_on=None, subscribed=True, expires_on=None):
        self.channel_id = channel_id
        self.channel_title = channel_title  # NB: Likely always None on init.
        self.added_on = added_on if added_on is not None else datetime.now(timezone.utc)
        self.subscribed = subscribed

        if expires_on:
            self.expires_on = expires_on
        else:
            # Only overwrite with None if not already set, to avoid losing an already valid one.
            if not self.expires_on:
                self.expires_on = None

        self.update_last_modified()

    def __repr__(self):
        return "<Channel(id='{my_id}', " \
               "channel_id='{channel_id}, " \
               "added_on='{added_on}', " \
               "last_modified='{last_modified}', " \
               "subscribed='{subscribed}', " \
               "expires_on='{expires_on}')>"\
            .format(my_id=self.id,
                    channel_id=self.channel_id,
                    added_on=self.added_on,
                    last_modified=self.last_modified,
                    subscribed=bool(self.subscribed),
                    expires_on=self.expires_on)

    def update_last_modified(self):
        self.last_modified = datetime.now(timezone.utc)

    def as_dict(self, stringify_datetime=False):
        return {
            "channel_id": self.channel_id,
            "added_on": self.added_on if not stringify_datetime else str(self.added_on),
            "last_modified": self.last_modified if not stringify_datetime else str(self.last_modified),
            "subscribed": bool(self.subscribed),
            "expires_on": self.expires_on if not stringify_datetime else str(self.expires_on)
        }
