### HealthCheck

Performs a health check on the Dedicated Server API. Allows passing additional data between Modded Dedicated Server and Modded Game Client.
This function requires no Authentication.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| ClientCustomData     | string              | Custom Data passed from the Game Client or Third Party service. Not used by vanilla Dedicated Servers |

Function Response Data:

| Property Name        | Property Type       | Description                                                                                                                           |
| -------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Health               | string              | "healthy" if tick rate is above ten ticks per second, "slow" otherwise                                                                |
| ServerCustomData     | string              | Custom Data passed from the Dedicated Server to the Game Client or Third Party service. Vanilla Dedicated Server returns empty string |

### QueryServerState

Retrieves the current state of the Dedicated Server. Does not require any input parameters.

Function Response Data:

| Property Name   | Property Type | Description                                                                                           |
| --------------- | ------------- | ----------------------------------------------------------------------------------------------------- |
| ServerGameState | string        | Current game state of the server                                                                      |

ServerGameState:

| Property Name       | Property Type | Description                                                                                           |
| ------------------- | ------------- | ----------------------------------------------------------------------------------------------------- |
| ActiveSessionName   | string        | Name of the currently loaded game session                                                             |
| NumConnectedPlayers | integer       | Number of the players currently connected to the Dedicated Server                                     |
| PlayerLimit         | integer       | Maximum number of the players that can be connected to the Dedicated Server                           |
| TechTier            | integer       | Maximum Tech Tier of all Schematics currently unlocked                                                |
| ActiveSchematic     | string        | Schematic currently set as Active Milestone                                                           |
| GamePhase           | string        | Current game phase. None if no game is running                                                        |
| IsGameRunning       | boolean       | True if the save is currently loaded, false if the server is waiting for the session to be created    |
| TotalGameDuration   | integer       | Total time the current save has been loaded, in seconds                                               |
| IsGamePaused        | boolean       | True if the game is paused. If the game is paused, total game duration does not increase              |
| AverageTickRate     | float         | Average tick rate of the server, in ticks per second                                                  |
| AutoLoadSessionName | string        | Name of the session that will be loaded when the server starts automatically                          |

### GetServerOptions

Retrieves currently applied server options and server options that are still pending application (because of needing session or server restart)
Does not require input parameters.

Function Response Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| ServerOptions        | map<string, string> | All current server option values. Key is the name of the option, and value is it's stringified value  |
| PendingServerOptions | map<string, string> | Server option values that will be applied when the session or server restarts                         |

### GetAdvancedGameSettings

Retrieves currently applied advanced game settings. Does not require input parameters.

Function Response Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| CreativeModeEnabled  | boolean             | True if Advanced Game Settings are enabled for the currently loaded session                           |
| AdvancedGameSettings | map<string, string> | Values of Advanced Game Settings. Key is the name of the setting, and value is it's stringified value |

### ApplyAdvancedGameSettings

Applies new values to the provided Advanced Game Settings properties. Will automatically enable Advanced Game Settings
for the currently loaded save if they are not enabled already.

Function Request Data:

| Property Name                | Property Type       | Description                                                                                           |
| ---------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| AppliedAdvancedGameSettings  | map<string, string> | Key is the name of the Advanced Game Setting, and the Value is the new setting value as string        |

### ClaimServer

Claims this Dedicated Server if it is not claimed. Requires InitialAdmin privilege level, which can only be acquired by attempting passwordless login
while the server does not have an Admin Password set, e.g. it is not claimed yet.
Function does not return any data in case of success, and the server is claimed. The client should drop InitialAdmin privileges after that
and use returned AuthenticationToken instead, and update it's cached server game state by calling QueryServerState.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| ServerName           | string              | New name of the Dedicated Server                                                                      |
| AdminPassword        | string              | Admin Password to set on the Dedicated Server, in plaintext                                           |

Function Response Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| AuthenticationToken  | string              | New Authentication Token that the Caller should use to drop Initial Admin privileges                  |

Possible errors:

| Error Code       | Description                                                                |
| ---------------- | -------------------------------------------------------------------------- |
| ServerClaimed   | Server has already been claimed                                            |

### RenameServer

Renames the Dedicated Server once it has been claimed. Requires Admin privileges.
Function does not return any data on success.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| ServerName           | string              | New name of the Dedicated Server                                                                      |

Possible errors:

| Error Code         | Description                                                                |
| ------------------ | -------------------------------------------------------------------------- |
| ServerNotClaimed | Server has not been claimed yet. Use ClaimServer function instead          |

### SetClientPassword

Updates the currently set Client Protection Password. This will invalidate all previously issued Client authentication tokens.
Pass empty string to remove the password, and let anyone join the server as Client.
Requres Admin privileges. Function does not return any data on success.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| Password             | string              | Client Password to set on the Dedicated Server, in plaintext                                          |

Possible errors:

| Error Code         | Description                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------- |
| ServerNotClaimed | Server has not been claimed yet. Use ClaimServer function instead before calling SetClientPassword |
| PasswordInUse    | Same password is already used as Admin Password                                                    |

### SetAdminPassword

Updates the currently set Admin Password. This will invalidate all previously issued Client and Admin authentication tokens.
Requires Admin privileges. Function does not return any data on success.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| Password             | string              | Admin Password to set on the Dedicated Server, in plaintext                                           |
| AuthenticationToken  | string              | New Admin authentication token to use, since the token used for this request will become invalidated  |

Possible errors:

| Error Code                  | Description                                                                                        |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| ServerNotClaimed          | Server has not been claimed yet. Use ClaimServer function instead                                  |
| CannotResetAdminPassword | Attempt to set Password to empty string. Admin Password cannot be reset                            |
| PasswordInUse             | Same password is already used as Client Protection Password                                        |

### SetAutoLoadSessionName

Updates the name of the session that the Dedicated Server will automatically load on startup. Does not change currently loaded session.
Requires Admin privileges. Function does not return any data on success.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| SessionName          | string              | Name of the session to automatically load on Dedicated Server startup                                 |

### RunCommand

Runs the given Console Command on the Dedicated Server, and returns it's output to the Console. Requires Admin privileges.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| Command              | string              | Command Line to run on the Dedicated Server                                                           |

Function Response Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| CommandResult        | string              | Output of the command executed, with \n used as line separator                                        |

### Shutdown

Shuts down the Dedicated Server. If automatic restart script is setup, this allows restarting the server to apply new settings or update.
Requires Admin privileges. Shutdowns initiated by remote hosts are logged with their IP and their token.
Function does not return any data on success, and does not take any parameters.

### ApplyServerOptions

Applies new Server Options to the Dedicated Server. Requires Admin privileges.
Function does not return any data on success.

Function Request Data:

| Property Name                | Property Type       | Description                                                                                   |
| ---------------------------- | ------------------- | --------------------------------------------------------------------------------------------- |
| UpdatedServerOptions         | map<string, string> | Key is the name of the Server Option, and the Value is the new value as string                |

### CreateNewGame

Creates a new session on the Dedicated Server, and immediately loads it. HTTPS API becomes temporarily unavailable when map loading is in progress   |
Function does not return any data on success.

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| NewGameData          | ServerNewGameData   | Parameters needed to create new game session                                                          |

ServerNewGameData:

| Property Name               | Property Type       | Description                                                                                                |
| --------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------- |
| SessionName                 | string              | Name of the session to create                                                                              |
| MapName                     | string              | Path Name to the Map Package to use as a map. If not specified, default level                              |
| StartingLocation            | string              | Name of the starting location to use. Leaving it empty will use random starting location                   |
| SkipOnboarding              | boolean             | Whenever the Onboarding should be skipped. Currently Onboarding is always skipped on the Dedicated Servers |
| AdvancedGameSettings        | map<string, string> | Advanced Game Settings to apply to the newly created session                                               |
| CustomOptionsOnlyForModding | map<string, string> | Custom Options to pass to the newly created session URL. Not used by vanilla Dedicated Servers             |

### SaveGame

Saves the currently loaded session into the new save game file named as the argument.
Requires Admin privileges. SaveName might be changed to satisfy file system restrictions on file names.
Function does not return any data on success.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| SaveName             | string              | Name of the save game file to create. Passed name might be sanitized                                  |

Possible errors:

| Error Code         | Description                                                                                        |
| ------------------ | -------------------------------------------------------------------------------------------------- |
| SaveGameFailed   | Failed to save the game. Additional information might be availble in errorMessage property         |

### DeleteSaveFile

Deletes the existing save game file from the server. Requires Admin privileges. SaveName might be changed to satisfy file system
restrictions on file names. Function does not return any data on success.

Function Request Data:

| Property Name        | Property Type       | Description                                                                                           |
| -------------------- | ------------------- | ----------------------------------------------------------------------------------------------------- |
| SaveName             | string              | Name of the save game file to delete. Passed name might be sanitized                                  |

Possible errors:

| Error Code              | Description                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------- |
| DeleteSaveFileFailed | Failed to delete the save game file. Additional information might be available in errorMessage property |

### DeleteSaveSession

Deletes all save files belonging to the specific session name. Requires Admin privileges. SessionName must be
a valid session name with at least one saved save game file belonging to it.
Function does not return any data on success.

Function Request Data:

| Property Name        | Property Type       | Description                                                         |
| -------------------- | ------------------- | ------------------------------------------------------------------- |
| SessionName          | string              | Name of the save session to delete                                  |

Possible errors:

| Error Code                 | Description                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| SessionNotFound          | Failed to find any save game files belonging to the given session                                       |
| DeleteSaveSessionFile | Failed to delete save session files. Additional information might be available in errorMessage property |

### EnumerateSessions

Enumerates all save game files available on the Dedicated Server. Requires Admin privileges. Function does not require any additional parameters.

Function Response Data:

| Property Name        | Property Type            | Description                                                         |
| -------------------- | ------------------------ | ------------------------------------------------------------------- |
| Sessions             | array<SessionSaveStruct> | List of sessions available on the Dedicated Server                  |
| CurrentSessionIndex  | integer                  | Index of the currently selected session in the list                 |

Possible errors:

| Error Code                 | Description                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| EnumerateSessionsFailed  | Failed to enumerate save sessions. Additional information might be available in errorMessage property   |

SessionSaveStruct:

| Property Name               | Property Type       | Description                                                                                                |
| --------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------- |
| SessionName                 | string              | Name of the save session                                                                                   |
| SaveHeaders                 | array<SaveHeader>   | All save game files belonging to this session                                                              |

SaveHeader:

| Property Name               | Property Type       | Description                                                                                                |
| --------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------- |
| SaveVersion                 | integer             | Version of the Save Game format this file was saved with                                                   |
| BuildVersion                | integer             | Changelist of the game or dedicated server this file was saved by                                          |
| SaveName                    | string              | Name of the save game file in the filesystem                                                               |
| MapName                     | string              | Path to the map package this save game file is based on                                                    |
| MapOptions                  | string              | Additional Map URL options this save game was saved with                                                   |
| SessionName                 | string              | Custom Options to pass to the newly created session URL. Not used by vanilla Dedicated Servers             |
| PlayDurationSeconds         | integer             | Amount of seconds the game has been running for in total since the session was created                     |
| SaveDateTime                | string              | Date and time on which the save game file was saved                                                        |
| IsModdedSave                | boolean             | True if this save game file was saved with mods                                                            |
| IsEditedSave                | boolean             | True if this save game file has been edited by third party tools                                           |
| IsCreativeModeEnabled       | boolean             | True if Advanced Game Settings are enabled for this save game                                              |

### LoadGame

Loads the save game file by name, optionally with Advanced Game Settings enabled. Requires Admin privileges.
Dedicated Server HTTPS API will become temporarily unavailable when save game is being loaded.
Function does not return any data on succcess.

Function Request Data:

| Property Name               | Property Type            | Description                                                                 |
| --------------------------- | ------------------------ | --------------------------------------------------------------------------- |
| SaveName                    | string                   | Name of the save game file to load                                          |
| EnableAdvancedGameSettings  | boolean                  | True if save game file should be loaded with Advanced Game Settings enabled |

Possible errors:

| Error Code                 | Description                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| SaveGameLoadFailed      | Failed to find the save game file with the given name on the Dedicated Server                           |

### UploadSaveGame

Uploads save game file to the Dedicated Server with the given name, and optionally immediately loads it.
Requires Admin privileges. If save file is immediately loaded, Dedicated Server HTTPS API will become temporarily unavailable until save game is loaded.
This function does not return any data on success.

This function requires multipart-encoded form data as it's body. The following multipart part names are allowed:

| Multipart Field            | Description                                                                                              |
| -------------------------- | -------------------------------------------------------------------------------------------------------- |
| data                       | Standard Request Data body for this request, encoded as utf-8 JSON. Note that this includes the envelope |
| saveGameFile               | File attachment containing the save game file. Contents of the file will be validated on the server      |

Function Request Data:

| Property Name               | Property Type            | Description                                                                 |
| --------------------------- | ------------------------ | --------------------------------------------------------------------------- |
| SaveName                    | string                   | Name of the save game file to create on the Dedicated Server                |
| LoadSaveGame                | boolean                  | True if save game file should be immediately loaded by the Dedicated Server |
| EnableAdvancedGameSettings  | boolean                  | True if save game file should be loaded with Advanced Game Settings enabled |

Possible errors:

| Error Code                 | Description                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| InvalidSaveGame          | Invalid save game file encoding, malformed header or corrupted contents                                 |
| UnsupportedSaveGame      | Save game file is too old to be loaded by the Dedicated Server, or is too new                           |
| FileSaveFailed           | Failed to save the save game file to the underlying file system                                         |
| SaveGameLoadFailed      | Failed to find the created save game file                                                               |

### DownloadSaveGame

Downloads save game with the given name from the Dedicated Server. Requires Admin privileges.
This function responds with the file attachment containing the save game file on success, and with normal error response in case of error.

Function Request Data:

| Property Name               | Property Type            | Description                                                                 |
| --------------------------- | ------------------------ | --------------------------------------------------------------------------- |
| SaveName                    | string                   | Name of the save game file to download from the Dedicated Server            |

Possible errors:

| Error Code                 | Description                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------- |
| FileNotFound             | Save game file with the provided name is not found on the Dedicated Server                              |
