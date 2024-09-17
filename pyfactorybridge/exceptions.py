class ServerError(Exception):
    pass


class ServerClaimed(Exception):
    pass


class ServerNotClaimed(Exception):
    pass


class PasswordInUse(Exception):
    pass


class CannotResetAdminPassword(Exception):
    pass


class SaveGameFailed(Exception):
    pass


class DeleteSaveFileFailed(Exception):
    pass


class DeleteSaveSessionFailed(Exception):
    pass


class SessionNotFound(Exception):
    pass


class EnumerateSessionFailed(Exception):
    pass


class SaveGameLoadFailed(Exception):
    pass


class InvalidSaveGame(Exception):
    pass


class UnsupportedSaveGame(Exception):
    pass


class FileSavedFailed(Exception):
    pass


class FileNotFound(Exception):
    pass

class PasswordlessLoginNotPossible(Exception):
    pass


ServerExceptions = {
    "file_not_found": FileNotFound,
    "file_save_failed": FileSavedFailed,
    "unsupported_save_game": UnsupportedSaveGame,
    "invalid_save_game": InvalidSaveGame,
    "save_game_load_failed": SaveGameLoadFailed,
    "enumerate_session_failed": EnumerateSessionFailed,
    "session_not_found": SessionNotFound,
    "delete_save_session_failed": DeleteSaveSessionFailed,
    "delete_save_file_failed": DeleteSaveFileFailed,
    "save_game_failed": SaveGameFailed,
    "cannot_reset_admin_password": CannotResetAdminPassword,
    "password_in_use": PasswordInUse,
    "server_not_claimed": ServerNotClaimed,
    "server_claimed": ServerClaimed,
    "server_error": ServerError,
    "passwordless_login_not_possible": PasswordlessLoginNotPossible,
}
