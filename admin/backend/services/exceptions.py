class InvalidBookingException(Exception):
    ...


class PermissionException(Exception):
    ...


class BannedUserException(Exception):
    ...


class ChatAlreadyExistsError(Exception):
    """Выбрасывается, если чат с таким invite_link уже существует."""
    pass


class InvalidInviteLinkError(Exception):
    """Выбрасывается, если строка invite_link не соответствует ожидаемому формату."""
    pass


class UnableToGetChatException(Exception):
    ...


class PasswordNeededException(Exception):
    ...


class UserHasNoProxyException(Exception):
    ...
