import json
from typing import Union

from sqlalchemy import desc, asc
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


def get_videos(stringify_datetime: bool = False,
               sort_by_col: str = "published_on", order_descending: bool = True) -> list:
    session = db_session()

    try:
        order_func = desc if order_descending else asc

        # Get all rows in Video table.
        query = session.query(Video).order_by(order_func(sort_by_col))

        videos_list = []
        for video in query.all():
            videos_list.append(video.as_dict(stringify_datetime))

        log.debug("Videos:\n{}".format(json.dumps(videos_list, indent=4)))

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        raise
    finally:
        session.close()

    return videos_list


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


def update_columns(base: Base, **kwargs):
    """
    Update DB row columns based on kwargs.

    :param base: Database Base object.
    :param kwargs: Columns
    :return:
    """
    if hasattr(base, "last_modified"):
        base.update_last_modified()

    for attr, value in kwargs.items():
        if hasattr(base, attr):
            if getattr(base, attr) != value:
                setattr(base, attr, value)


def update_video(video_id: str, **kwargs):
    # Create a Session
    session = db_session()
    try:
        video = session.query(Video).filter(Video.video_id == video_id).one()

        update_columns(video, **kwargs)

        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        session.rollback()
        raise
    finally:
        session.close()


def add_or_update_video(video_id, **kwargs):
    """
    Adds Video row to DB or updates existing one.
    :return:
    """
    # Create a Session
    session = db_session()
    try:
        # Check if entry already exists by getting the first item in the query list.
        video_record: Union[Video, None] = session.query(Video).filter(Video.video_id == video_id).first()

        if video_record:
            log.db_info("Update Video '{video_id}'.".format(video_id=video_id))
            video_dict = video_record.as_dict()
            log.debug2(video_dict)
            update_columns(video_record, **kwargs)
        else:
            log.db_info("Add Video '{video_id}'.".format(video_id=video_id))
            video = Video(video_id=video_id, **kwargs)
            session.add(video)

        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        session.rollback()
        raise
    finally:
        session.close()


def add_or_update_row(base: Union[Video, Channel], filter_criterion, **kwargs):
    """
    Adds Video/Channel row to DB or updates existing one.

    NB: **EXPERIMENTAL**
    :return:
    """
    # Create a Session
    session = db_session()
    try:
        # Check if entry already exists by getting the first item in the query list.
        if isinstance(base, Video):
            record: Union[Base, None] = session.query(Video).filter_by(video_id=filter_criterion).first()
        elif isinstance(base, Channel):
            record: Union[Base, None] = session.query(Channel).filter_by(channel_id=filter_criterion).first()
        else:
            raise SQLAlchemyError("add_or_update_row called with unsupported Base '{basename}'".format(
                basename=base.__tablename__))

        if record:
            log.db_info("Update {basename} '{flt}'.".format(basename=base.__tablename__, flt=filter_criterion))
            record_dict = record.as_dict()
            log.debug2(record_dict)
            update_columns(record, **kwargs)
        else:
            log.db_info("Add {basename} '{flt}'.".format(basename=base.__tablename__, flt=filter_criterion))
            if isinstance(base, Video):
                row = Video(**kwargs)
            elif isinstance(base, Channel):
                row = Channel(**kwargs)
            else:
                raise SQLAlchemyError("add_or_update_row called with unsupported Base '{basename}'".format(
                    basename=base.__tablename__))

            session.add(row)

        session.commit()
    except SQLAlchemyError:
        log.exception(SQLAlchemyError)
        session.rollback()
        raise
    finally:
        session.close()
