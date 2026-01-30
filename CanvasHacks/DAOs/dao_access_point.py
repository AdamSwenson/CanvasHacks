from sqlalchemy.util import classproperty

from CanvasHacks.DAOs.sqlite_dao import SqliteDAO
from CanvasHacks.DAOs.sqlite_message_dao import QueueSqliteDAO


class DAOHolder(object):
    """
    This allows for there to be one set of sessions / engines
    for all processes to access
    """

    _message_queue_dao = None

    unit_daos = {}

    @classmethod
    def _initialize_message_queue(cls):
        cls._message_queue_dao = QueueSqliteDAO()

    @classmethod
    def _initialize_unit_dao(cls, unit_number):
        cls.unit_daos[unit_number] = SqliteDAO(unit_number)
        print(f"Created main dao for unit {unit_number}")

    @classproperty
    def message_queue_dao(cls):
        if cls._message_queue_dao is None:
            cls._initialize_message_queue()
        return cls._message_queue_dao

    @classmethod
    def get_unit_dao(cls, unit_number):
        if unit_number not in cls.unit_daos.keys():
            cls._initialize_unit_dao(unit_number)
        return cls.unit_daos[unit_number]