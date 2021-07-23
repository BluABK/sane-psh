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


def row_exists(table_obj: Base, **kwargs):
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


# def drop_table(table_name, engine):
#     Base = declarative_base()
#     metadata = MetaData()
#     metadata.reflect(bind=engine)
#     table = metadata.tables[table_name]
#     if table is not None:
#         Base.metadata.drop_all(engine, [table], checkfirst=True)

def wipe_table(table):
    # Create a Session
    session = db_session()

    try:
        session.query(table).delete()

        session.commit()
    except SQLAlchemyError:
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
        session.rollback()
        raise
    finally:
        session.close()


def get_channel(channel_id: str) -> dict:
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


def get_channels(stringify_datetime: bool = False) -> dict:
    session = db_session()

    try:
        # Get all rows in Channel table.
        channel_objs: dict = session.query(Channel).all()
        channels_dict = {}
        for channel in channel_objs:
            channels_dict[channel.channel_id] = channel.as_dict(stringify_datetime)
        log.debug("channels")
        log.debug(channels_dict)

        # Commit transaction (NB: makes detached instances expire)
        session.commit()
    except SQLAlchemyError:
        raise
    finally:
        session.close()

    return channels_dict


def get_video(video_id: str) -> dict:
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


def del_row_by_filter(table_obj: Base, **kwargs):
    """
    Delete row filtered by provided kwarg and don’t synchronize the session.

    This option is the most efficient and is reliable once the session is expired,
    which typically occurs after a commit(), or explicitly using expire_all().

    Before the expiration, objects may still remain in the session which were
    in fact deleted which can lead to confusing results if they are accessed
    via get() or already loaded collections.

    https://www.kite.com/python/docs/sqlalchemy.orm.query.Query.delete
    :param table_obj:
    :param kwargs:
    :return:
    """
    # Create a Session
    session = db_session()
    try:
        rows = session.query(table_obj).filter_by(**kwargs)
        rows.delete(synchronize_session=False)
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
