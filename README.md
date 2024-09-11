<p align="center">
<img src="assets/icon.png">

<p align="center">➡️ <a href="methods.md">Method References</a> ⬅️</p>

<p align="center">Satisfactory Dedicated Server HTTP API Python wrapper<br>
<code>pip install pyfactorybridge</code>
</p>

# Overview
This is a Python wrapper for the Satisfactory Dedicated Server HTTP API. It is designed to make it easier to interact with the API and to provide a more Pythonic interface.

# Features
Direct 1:1 implementation to the offical documentation. *Most* API endpoints supported (bar downloading & uploading saves, and some other ways of authenticating). No need to manually construct URLs or handle HTTP requests. Easy to use and understand.

# Demo

*All methods are documented in the [methods.md](methods.md) file.*

```py
from pyfactorybridge import API
from pyfactorybridge.exceptions import SaveGameFailed

satisfactory = API(address="XXXX:7777", password="XXXX")

try:
    satisfactory.save_game(SaveName="Test")
except SaveGameFailed as error:
    print("Could not save game!")

print(satisfactory.get_server_options())

satisfactory.shutdown()
```

# ToDo

- Update documentation to reflect error exceptions
- Add support for more authentication methods
- Implement more logging and catch request errors
- Add support for SSL certifications to avoid using `verify=false`
- Add support for downloading and uploading games
