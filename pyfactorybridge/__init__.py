import logging
from json import dumps
from pathlib import Path
from requests import Session
from requests.exceptions import ConnectionError, Timeout
from typing_extensions import Any

from pyfactorybridge import exceptions
from pyfactorybridge.exceptions import ServerExceptions, ServerError
from pyfactorybridge.authentication import BearerAuth

#### SSL VERIFICATION ####
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(InsecureRequestWarning)

from pyfactorybridge.ssl_adapter import FactoryGameSSLAdapter
##########################


class API:
    def __init__(
        self,
        address: str,
        password: str | None = None,
        privilege_level: str = "Administrator",
        token: str | None = None,
        verify_ssl_chain_path: str | None = None,
        enable_http_request_debugging: bool = False,
    ):
        self.URL = f"https://{address}/api/v1/"
        self.auth = None

        self.session = Session()

        if verify_ssl_chain_path:
            ssl_http_adapter = FactoryGameSSLAdapter(verify_ssl_chain_path)
            self.session.mount("https://", ssl_http_adapter)

        if enable_http_request_debugging:
            self.__enable_http_request_debugging()

        if (
            self.get_server_health()["health"] == "slow"
        ):  # Also checks if the server is reachable
            logging.error("Server is slow to respond 🐌")

        if token:
            self.renew_auth(
                method="token", value=token, permissions=privilege_level
            )
        elif password:
            self.renew_auth(
                method="password", value=password, permissions=privilege_level
            )
        else:
            self.renew_auth()

    def __enable_http_request_debugging(self):
        import http.client as http_client

        http_client.HTTPConnection.debuglevel = 1

        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def __build_request_data(
        self, function: str, properties: dict | None = None
    ) -> dict:
        request_data = {"data": {"clientCustomData": ""}, "function": function}
        if isinstance(properties, dict):
            for property_name, property_value in properties.items():
                request_data["data"][property_name] = property_value
        return request_data

    def __request(
        self,
        function: str,
        properties: dict | None = None,
        multiparts: dict | None = None,
    ) -> Any:
        request_data = self.__build_request_data(function, properties)
        http_method_kwargs = {}

        if multiparts is None:
            # Simple application/json request
            http_method_kwargs["json"] = request_data
        else:
            # multipart/form-data request
            if "data" not in multiparts:
                multiparts["data"] = (
                    # Multipart file name
                    None,
                    # Multipart content (byte-like)
                    dumps(request_data),
                    # Content-Type
                    "application/json",
                )
            http_method_kwargs["files"] = multiparts

        try:
            response_data = self.session.post(
                self.URL, verify=False, auth=self.auth, **http_method_kwargs
            )

            try:
                response_data = response_data.json()
            except ValueError:
                return response_data.content

            if error := response_data.get("errorCode"):
                raise ServerExceptions.get(error, ServerError)(
                    response_data.get("errorMessage")
                )

            return response_data["data"]

        except (ConnectionError, Timeout):
            raise ServerError("The server could not be reached")

    def renew_auth(
        self,
        method: str | None = None,
        value: str | None = None,
        permissions: str = "Administrator",
    ):
        """Renew the authentication token based on the provided method."""

        if permissions not in [
            "Administrator",
            "Client",
            "APIToken",
            "NotAuthenticated",
        ]:
            raise ValueError("Invalid minimum privilege level provided.")

        if method == "token":
            logging.info("API token provided.")
            self.auth = self.__auth_from_api_token(value)
        elif method == "password":
            logging.warning("Password provided instead of API token.")
            self.auth = self.__auth_from_password(
                value, MinimumPrivilegeLevel=permissions
            )
        else:
            logging.error("No password provided, trying passwordless login.")
            self.auth = self.__auth_from_passwordless()

            if self.auth:
                logging.info("Passwordless login successful. Please claim the server.")

            else:
                logging.error("Passwordless login failed. Using no authentication.")

        logging.info("API initialized")

    def __auth_from_password(
        self, Password, MinimumPrivilegeLevel="Administrator"
    ) -> BearerAuth | None:
        response_data = self.__request(
            function="PasswordLogin",
            properties={
                "password": Password,
                "minimumPrivilegeLevel": MinimumPrivilegeLevel,
            },
        )

        if token := response_data.get("authenticationToken"):
            return BearerAuth(token)

    def __auth_from_passwordless(self) -> BearerAuth | None:
        try:
            response_data = self.__request(
                function="PasswordlessLogin",
                properties={"minimumPrivilegeLevel": "InitialAdmin"},
            )

            if token := response_data.get("authenticationToken"):
                return BearerAuth(token)
        except (exceptions.PasswordlessLoginNotPossible):
            pass

        return None

    def __auth_from_api_token(self, Token) -> BearerAuth:
        return BearerAuth(Token)

    ### Methods ###

    def get_server_health(self) -> dict[str, str]:
        """Check the health of the server. Returns "healthy" if tick rate is above ten ticks per second, "slow" otherwise"""
        return self.__request(function="HealthCheck")

    def query_server_state(self) -> dict[str, str]:
        """Query the current state of the server"""
        return self.__request(function="QueryServerState")

    def get_server_options(self) -> dict[str, str]:
        """Get server options. Returns a dictionary of server options, pending server options and their values."""
        return self.__request(function="GetServerOptions")

    def get_advanced_game_settings(self) -> dict[str, str]:
        """Get advanced game settings. Returns a dictionary of advanced game settings and if creative mode is enabled"""
        return self.__request(function="GetAdvancedGameSettings")

    def apply_advanced_game_settings(
        self, SettingName: str, SettingValue: str
    ) -> dict[str, str]:
        """Applies advanced game setting. Doesn't return anything."""
        return self.__request(
            function="ApplyAdvancedGameSettings", properties={SettingName: SettingValue}
        )

    def claim_server(self, ServerName: str, AdminPassword: str) -> str:
        """Claims the server. Also reauthenticates the user."""
        data = self.__request(
            function="ClaimServer",
            properties={"ServerName": ServerName, "AdminPassword": AdminPassword},
        )

        self.renew_auth(
            method="token",
            value=data["authenticationToken"],
            permissions="Administrator",
        )

        return data

    def rename_server(self, ServerName: str) -> dict[str, str]:
        """Renames the server"""
        return self.__request(
            function="RenameServer", properties={"ServerName": ServerName}
        )

    def set_client_password(self, ClientPassword: str) -> dict[str, str]:
        """Sets the client password. Returns nothing."""
        return self.__request(
            function="SetClientPassword", properties={"Password": ClientPassword}
        )

    def set_admin_password(
        self, AdminPassword: str, AuthenticationToken: str
    ) -> dict[str, str]:
        """Sets the admin password. Returns nothing."""
        return self.__request(
            function="SetAdminPassword",
            properties={
                "Password": AdminPassword,
                "AuthenticationToken": AuthenticationToken,
            },
        )

    def set_auto_load_session_name(self, SessionName: str) -> dict[str, str]:
        """Sets the auto load session name. Returns nothing."""
        return self.__request(
            function="SetAutoLoadSessionName", properties={"SessionName": SessionName}
        )

    def run_command(self, Command: str) -> dict[str, str]:
        return self.__request(function="RunCommand", properties={"Command": Command})

    def shutdown(self) -> dict[str, str]:
        """Shuts down the server."""
        return self.__request(function="Shutdown")

    def apply_server_options(self, UpdatedServerOptions: dict) -> dict[str, str]:
        """Applies server options. Requires a JSON string of options."""
        return self.__request(
            function="ApplyServerOptions",
            properties={"UpdatedServerOptions": UpdatedServerOptions},
        )

    def create_new_game(self, NewGameData: str) -> dict[str, str]:
        """Creates a new game."""
        return self.__request(
            function="CreateNewGame", properties={"NewGameData": NewGameData}
        )

    def save_game(self, SaveName: str) -> dict[str, str]:
        """Saves the current game state."""
        return self.__request(function="SaveGame", properties={"SaveName": SaveName})

    def delete_save_file(self, SaveName: str) -> dict[str, str]:
        """Deletes a save file."""
        return self.__request(
            function="DeleteSaveFile", properties={"SaveName": SaveName}
        )

    def deletion_save_session(self, SessionName: str) -> dict[str, str]:
        """Deletes a save session."""
        return self.__request(
            function="DeleteSaveSession", properties={"SessionName": SessionName}
        )

    def enumerate_sessions(self) -> dict[list[dict], int]:
        """Enumerates all sessions on the server. Returns a list of session names."""
        return self.__request(function="EnumerateSessions")

    def load_game(
        self, SaveName: str, EnableAdvancedGameSettings: bool
    ) -> dict[str, str]:
        """Loads a game from a save name."""
        return self.__request(
            function="LoadGame",
            properties={
                "SaveName": SaveName,
                "EnableAdvancedGameSettings": EnableAdvancedGameSettings,
            },
        )

    def upload_save_game(
        self,
        save_file_path: str,
        SaveName: str | None = None,
        LoadSaveGame: bool = False,
        EnableAdvancedGameSettings: bool = False,
    ) -> dict[str, str]:
        """Uploads a save game file to the server. Requires the path to the save file."""
        try:
            with open(save_file_path, "rb") as save_file_handle:
                save_file_path_obj = Path(save_file_path)
                multiparts = {
                    "saveGameFile": (
                        # Save file basename (including .sav)
                        save_file_path_obj.name,
                        # Save file content
                        save_file_handle.read(),
                        # Content-Type
                        "application/octet-stream",
                    )
                }
                return self.__request(
                    function="UploadSaveGame",
                    properties={
                        "SaveName": SaveName
                        or save_file_path_obj.stem,  # Save file name without file extension
                        "LoadSaveGame": LoadSaveGame,
                        "EnableAdvancedGameSettings": EnableAdvancedGameSettings,
                    },
                    multiparts=multiparts,
                )
        except (FileNotFoundError, PermissionError, OSError):
            raise Exception(f"Cannot read path: {save_file_path}")

    def download_save_game(self, SaveName: str, save_file_path: str) -> None:
        """Downloads a save game from the server."""
        try:
            with open(save_file_path, "wb") as save:
                save.write(
                    self.__request(
                        function="DownloadSaveGame", properties={"SaveName": SaveName}
                    )
                )
        except (FileNotFoundError, PermissionError, OSError):
            raise Exception(f"Cannot write to file path: {save_file_path}")


def main():
    raise SystemExit("This is a library, not a standalone script.")
