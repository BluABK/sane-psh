from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, VARCHAR, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    channel_id = Column(VARCHAR)
    # NB: Channel title can only be acquired when a video belonging to this Channel shows up,
    #     as it isn't included in the subscribe GET request that init this object.
    channel_title = Column(VARCHAR)
    videos = relationship("Video", back_populates='channel')
    # DB entry creation date.
    added_on = Column(DateTime)
    # DB entry last modified date.
    last_modified = Column(DateTime)
    subscribed = Column(Boolean)
    verify_token = Column(VARCHAR)
    hmac_secret = Column(VARCHAR)

    def __init__(self, channel_id,
                 channel_title=None, added_on=None, subscribed=True,
                 verify_token=None, hmac_secret=None):
        self.channel_id = channel_id
        self.channel_title = channel_title  # NB: Likely always None on init.
        self.added_on = added_on if added_on is not None else datetime.now(timezone.utc)
        self.subscribed = subscribed
        self.verify_token = verify_token
        self.hmac_secret = hmac_secret
        self.update_last_modified()

    def __repr__(self):
        return "<Channel(id='{my_id}', " \
               "channel_id='{channel_id}, " \
               "added_on='{added_on}', " \
               "last_modified='{last_modified}', " \
               "subscribed='{subscribed}', " \
               "verify_token='{verify_token}', " \
               "hmac_secret='{hmac_secret}')>"\
            .format(my_id=self.id,
                    channel_id=self.channel_id,
                    added_on=self.added_on,
                    last_modified=self.last_modified,
                    subscribed=bool(self.subscribed),
                    verify_token=self.verify_token,
                    hmac_secret=self.hmac_secret)

    def update_last_modified(self):
        self.last_modified = datetime.now(timezone.utc)

    def as_dict(self):
        return {
            "channel_id": self.channel_id,
            "added_on": self.added_on,
            "last_modified": self.last_modified,
            "subscribed": bool(self.subscribed),
            "verify_token": self.verify_token,
            "hmac_secret": self.hmac_secret
        }
