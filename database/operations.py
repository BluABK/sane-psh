from sqlalchemy.exc import SQLAlchemyError

from database import db_session
from database.models.channel import Channel
from database.models.video import Video
from handlers.log_handler import create_logger

log = create_logger(__name__)


def row_exists(table_obj, **kwargs):
    # Create a Session
    session = db_session()
    exists = None
    try:
        exists = session.query(table_obj.id).filter_by(**kwargs).scalar() is not None

        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()
        return exists


def add_row(db_row):
    # Create a Session
    session = db_session()
    try:
        session.add(db_row)
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def get_channel(channel_id) -> dict:
    session = db_session()

    try:
        # Get the first item in the list of queries.
        channel_dict: dict = session.query(Channel).filter(Channel.channel_id == channel_id)[0].as_dict()

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        raise
    finally:
        session.close()

    return channel_dict


def get_channels() -> dict:
    session = db_session()

    try:
        # Get all rows in Channel table.
        channel_objs: dict = session.query(Channel).all()
        channels_dict = {}
        for channel in channel_objs:
            channels_dict[channel.channel_id] = channel.as_dict()
        log.debug("channels")
        log.debug(channels_dict)

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        raise
    finally:
        session.close()

    return channels_dict


def get_video(video_id) -> dict:
    session = db_session()

    try:
        # Get the first item in the list of queries.
        video_dict: dict = session.query(Video).filter(Video.video_id == video_id)[0].as_dict()

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        raise
    finally:
        session.close()

    return video_dict


def del_row_by_filter(table_obj, **kwargs):
    # Create a Session
    session = db_session()
    try:
        session.query(table_obj.id).filter_by(**kwargs).delete()
        session.commit()
    except SQLAlchemyError:
        session.rollback()
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
