from typing import Union
from sqlalchemy.exc import SQLAlchemyError

from database import engine, db_session, Base
from database.models.channel import Channel
from database.models.video import Video
from handlers.log_handler import create_logger

log = create_logger(__name__)

# List of all DB tables (used for sanity checks)
TABLES = [Channel, Video]


def db_is_empty():
    # Create a Session
    session = db_session()
    is_empty = True
    for table in TABLES:
        if session.query(table).first() is not None:
            log.info("DB is not empty: Query first() for table '{}' is not None.".format(table.__tablename__))
            is_empty = False

    return is_empty


def wipe_table(table):
    # Create a Session
    session = db_session()

    try:
        session.query(table).delete()

        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        session.rollback()
        raise
    finally:
        session.close()
        return True


def wipe_db():
    # Create a Session
    session = db_session()

    try:
        for table in TABLES:
            session.query(table).delete()

        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        session.rollback()
        raise
    finally:
        session.close()
        return True


def add_row(db_row: Base):
    # Create a Session
    session = db_session()
    try:
        session.add(db_row)
        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        session.rollback()
        raise
    finally:
        session.close()


def get_channel(channel_id: str) -> dict:
    session = db_session()
    channel_dict: Union[dict, None] = None

    try:
        # Get the first item in the list of queries.
        channel_record: Union[Channel, None] = session.query(Channel).filter(Channel.channel_id == channel_id).first()
        if channel_record:
            channel_dict = channel_record.as_dict()

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        raise
    finally:
        session.close()

    return channel_dict


def get_channels(stringify_datetime: bool = False) -> dict:
    session = db_session()

    try:
        # Get all rows in Channel table.
        channel_objs: dict = session.query(Channel).all()
        channels_dict = {}
        for channel in channel_objs:
            channels_dict[channel.channel_id] = channel.as_dict(stringify_datetime)
            channels_dict[channel.channel_id].pop("channel_id")
        log.debug("channels:")
        log.debug(channels_dict)

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        raise
    finally:
        session.close()

    return channels_dict


def get_video(video_id: str) -> dict:
    session = db_session()
    video_dict: Union[dict, None] = None
    try:
        # Get the first item in the list of queries.
        video_record: Union[Video, None] = session.query(Video).filter(Video.video_id == video_id).first()
        if video_record:
            video_dict = video_record.as_dict()

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        raise
    finally:
        session.close()

    return video_dict


def get_videos(stringify_datetime: bool = False) -> dict:
    session = db_session()

    try:
        # Get all rows in Video table.
        video_objs: dict = session.query(Video).all()
        videos_dict = {}
        for video in video_objs:
            videos_dict[video.video_id] = video.as_dict(stringify_datetime)
            videos_dict[video.video_id].pop("video_id")
        log.debug("videos:")
        log.debug(videos_dict)

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        raise
    finally:
        session.close()

    return videos_dict


def del_video_by_id(video_id: str):
    # Create a Session
    session = db_session()
    try:
        session.query(Video).filter(Video.video_id == video_id).delete()
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        log.exception(SQLAlchemyError)
        raise
    finally:
        session.close()


def update_channel(channel_id: str, **kwargs):
    # Create a Session
    session = db_session()
    try:
        channel = session.query(Channel).filter(Channel.channel_id == channel_id).one()

        channel.update_last_modified()

        for attr, value in kwargs.items():
            if hasattr(channel, attr):
                if getattr(channel, attr) != value:
                    setattr(channel, attr, value)

        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def update_video(video_id: str, **kwargs):
    # Create a Session
    session = db_session()
    try:
        video = session.query(Video).filter(Video.video_id == video_id).one()

        video.update_last_modified()

        for attr, value in kwargs.items():
            if hasattr(video, attr):
                if getattr(video, attr) != value:
                    setattr(video, attr, value)

        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()
