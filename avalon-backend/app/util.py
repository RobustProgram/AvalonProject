"""
File full of utility functions to help reduce code bloat
"""
import namegenerator
from flask_socketio import emit
from . import constants


def get_name(data=None):
    """Get name specified by the user

    Args:
        data (dict, optional): [description]. Defaults to None.

    Returns:
        str: Either the name specified by the user or a randomly generated name
    """
    if not data:
        return namegenerator.gen()

    name = data.get("name", None)

    if not name:
        name = namegenerator.gen()

    return name


def data_required(custom_message=None):
    """Wrapper to lock down an event and prevent it from running if data has not been sent

    Args:
        custom_message (str, optional): The message that should be returned to the user.
                                        Defaults to None.
    """

    def decorator(func):
        """Real decorator that is hidden"""

        def wrapper(*args):
            message = (
                custom_message or "You can not call this event without sending data."
            )

            if not args:
                emit(
                    constants.SYS_MESSAGE,
                    {"error": message},
                )
                return
            func(*args)

        return wrapper

    return decorator
