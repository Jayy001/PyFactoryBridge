import requests
import logging

from pyfactorybridge.exceptions import ServerExceptions, ServerError
from pyfactorybridge.authentication import BearerAuth

from typing_extensions import Any

#### SSL VERIFICATION ####

import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##########################


class API:
    def __init__(self, address, password=None):
        self.URL = f"https://{address}/api/v1/"
        self.auth = None

        if (
            self.get_server_health()["health"] == "slow"
        ):  # Also checks if the server is reachable
            logging.error("Server is slow to respond 🐌")

        if password:
            self.auth = self.authorise(password)
        else:
            logging.error("No password provided, some functions may not work.")

    def __request(self, function, properties={}) -> dict[Any]:
        request_data = {"data": {"clientCustomData": ""}, "function": function}

        for property_name, property_value in properties.items():
            request_data["data"][property_name] = property_value

        try:
            response_data = requests.post(
                self.URL,
                verify=False,
                json=request_data,
                auth=self.auth if self.auth else None,
                headers={"Content-Type": "application/json"},
            )

            if response_data.text:
                response_data = response_data.json()
            else:
                return {}

            if error := response_data.get("errorCode"):
                raise ServerExceptions.get(error, ServerError)(
                    response_data.get("errorMessage")
                )

            return response_data["data"]

        except requests.exceptions.Timeout:
            raise ServerError("The server could not be reached")

    def authorise(self, Password) -> BearerAuth | None:
        response_data = self.__request(
            function="PasswordLogin",
            properties={"password": Password, "minimumPrivilegeLevel": "Administrator"},
        )

        if (token := response_data.get("authenticationToken")) is not None:
            return BearerAuth(token)

    ### Methods ###

    def get_server_health(self) -> dict[str, str]:
        return self.__request(function="HealthCheck")

    def query_server_state(self) -> dict[str, str]:
        return self.__request(function="QueryServerState")

    def get_server_options(self) -> dict[str, str]:
        return self.__request(function="GetServerOptions")

    def get_advanced_game_settings(self) -> dict[str, str]:
        return self.__request(function="GetAdvancedGameSettings")

    def apply_advanced_game_settings(self, SettingName, SettingValue) -> dict[str, str]:
        return self.__request(
            function="ApplyAdvancedGameSettings", properties={SettingName: SettingValue}
        )

    def claim_server(self, ServerName, AdminPassword) -> dict[str, str]:
        return self.__request(
            function="ClaimServer",
            properties={"ServerName": ServerName, "AdminPassword": AdminPassword},
        )

    def rename_server(self, ServerName) -> dict[str, str]:
        return self.__request(
            function="RenameServer", properties={"ServerName": ServerName}
        )

    def set_client_password(self, ClientPassword) -> dict[str, str]:
        return self.__request(
            function="SetClientPassword", properties={"Password": ClientPassword}
        )

    def set_admin_password(self, AdminPassword, AuthenticationToken) -> dict[str, str]:
        return self.__request(
            function="SetAdminPassword",
            properties={
                "Password": AdminPassword,
                "AuthenticationToken": AuthenticationToken,
            },
        )

    def set_auto_load_session_name(self, SessionName) -> dict[str, str]:
        return self.__request(
            function="SetAutoLoadSessionName", properties={"SessionName": SessionName}
        )

    def run_command(self, Command) -> dict[str, str]:
        return self.__request(function="RunCommand", properties={"Command": Command})

    def shutdown(self) -> dict[str, str]:
        return self.__request(function="Shutdown")

    def apply_server_options(self, UpdatedServerOptions) -> dict[str, str]:
        return self.__request(
            function="ApplyServerOptions",
            properties={"UpdatedServerOptions": UpdatedServerOptions},
        )

    def create_new_game(self, NewGameData) -> dict[str, str]:
        return self.__request(
            function="CreateNewGame", properties={"NewGameData": NewGameData}
        )

    def save_game(self, SaveName) -> dict[str, str]:
        return self.__request(function="SaveGame", properties={"SaveName": SaveName})

    def delete_save_file(self, SaveName) -> dict[str, str]:
        return self.__request(
            function="DeleteSaveFile", properties={"SaveName": SaveName}
        )

    def deletion_save_session(self, SessionName) -> dict[str, str]:
        return self.__request(
            function="DeleteSaveSession", properties={"SessionName": SessionName}
        )

    def enumerate_sessions(self) -> dict[str, str]:
        return self.__request(function="EnumerateSessions")

    def load_game(self, SaveName, EnableAdvancedGameSettings) -> dict[str, str]:
        return self.__request(
            function="LoadGame",
            properties={
                "SaveName": SaveName,
                "EnableAdvancedGameSettings": EnableAdvancedGameSettings,
            },
        )

    def upload_save_game(self, data) -> None:
        raise NotImplementedError

    def download_save_game(self, SaveName) -> None:
        raise NotImplementedError


def main():
    raise SystemExit("This is a library, not a standalone script.")
