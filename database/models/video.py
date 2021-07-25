from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, VARCHAR, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Video(Base):
    __tablename__ = 'video'
    id = Column(Integer, primary_key=True)
    channel_id = Column(VARCHAR, ForeignKey('channel.channel_id'))
    channel = relationship("Channel", back_populates='videos')
    video_id = Column(VARCHAR, unique=True)
    video_title = Column(VARCHAR)
    # YouTube entry publish date.
    published_on = Column(DateTime)
    # YouTube entry last update date.
    updated_on = Column(DateTime)
    # DB entry creation date.
    added_on = Column(DateTime)
    # DB entry last modified date.
    last_modified = Column(DateTime)

    def __init__(self, video_id, channel_id, video_title, published_on, updated_on, added_on=None):
        self.video_id = video_id
        self.channel_id = channel_id
        self.video_title = video_title
        self.published_on = published_on
        self.updated_on = updated_on
        self.added_on = added_on if added_on is not None else datetime.now(timezone.utc)
        self.update_last_modified()

    def __repr__(self):
        return "<Video(id='{my_id}', " \
               "video_id='{video_id}, " \
               "channel_id='{channel_id}, " \
               "video_title='{video_title}', " \
               "published_on='{published_on}', " \
               "updated_on='{updated_on}', " \
               "added_on='{added_on}', " \
               "last_modified='{last_modified}')>" \
            .format(my_id=self.id,
                    channel_id=self.channel_id,
                    video_id=self.video_id,
                    video_title=self.video_title,
                    published_on=self.published_on,
                    updated_on=self.updated_on,
                    added_on=self.added_on,
                    last_modified=self.last_modified)

    def update_last_modified(self):
        self.last_modified = datetime.now(timezone.utc)

    def as_dict(self, stringify_datetime=False):
        return {
            "video_id": self.video_id,
            "channel_id": self.channel_id,
            "video_title": self.video_title,
            "published_on": self.published_on if not stringify_datetime else str(self.published_on),
            "updated_on": self.updated_on if not stringify_datetime else str(self.updated_on),
            "added_on": self.added_on if not stringify_datetime else str(self.added_on),
            "last_modified": self.last_modified if not stringify_datetime else str(self.last_modified)
        }
