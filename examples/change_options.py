from pyfactorybridge import API

satisfactory = API(address="XXXXXXX:7777", password="XXXXXXXX")

print(satisfactory.get_server_options()["serverOptions"]["FG.AutosaveInterval"])

satisfactory.apply_server_options({"FG.AutosaveInterval": "150"})

print(satisfactory.get_server_options()["serverOptions"]["FG.AutosaveInterval"])
