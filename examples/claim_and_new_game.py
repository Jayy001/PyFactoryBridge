#!/usr/bin/env python3
"""
Used after running a server for the first time (or after clearing saved data: https://satisfactory.wiki.gg/wiki/Dedicated_servers/Configuration_files#Overview)
Claims the server with the provided name and admin password, prints the authentication token created, and creates a 
new game on the server with a random starting location, printing a json object with server info afterwards
Options can also be set with comma separated key=value
"""

from pyfactorybridge import API
from pyfactorybridge.exceptions import ServerError
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from json import dumps
from sys import exit, stderr

def main():
    parser = ArgumentParser(description=__doc__, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument("password", help="the desired server admin password")
    parser.add_argument("address", default="localhost:7777", nargs="?", help="the address of the server to connect to")
    parser.add_argument("--token", help="If server is already claimed, specifies the authentication token to be used")
    parser.add_argument("--server-name", default="My First Server", help="Sets the Server Name (shown in the Server Manager list). Defaults to 'My First Server'")
    parser.add_argument("--session-name", default="My First Game", help="Sets the Session Name (shown in the Server Status screen after selecting the server to join). Defaults to 'My First Game'")
    parser.add_argument("--options", help="Sets server options before starting the game (comma separated key=value). e.g: FG.DSAutoPause=false")
    args = parser.parse_args()

    token = args.token
    if not token:
        server = API(address=args.address)
        try:
            token = server.claim_server(args.server_name, args.password)["authenticationToken"]
        except ServerError:
            print("Couldn't authenticate to claim server, is the server already claimed? Provide a token with --token", file=stderr)
            exit(2)
    else:
        server = API(address=args.address, token=token)

    print(f"Authenticating with token: {token}", file=stderr)
    options = server.get_server_options()["serverOptions"]
    if args.options:
        for option in args.options.split(","):
            k,v = option.split("=",1)
            options[k] = v
    _ = server.apply_server_options(options)
    _ = server.create_new_game({"SessionName": args.session_name})
    state = s.query_server_state()
    state["options"] = options
    print(dumps(state, indent=4))
    return 0

if __name__ == "__main__":
    exit(main())
