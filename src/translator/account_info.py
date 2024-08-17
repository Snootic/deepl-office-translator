import deepl

class Account():
    def __init__(self,api_key:str) -> None:
        self.API_KEY = api_key

    def check_usage(self) -> list:
        usage = deepl.Translator(self.API_KEY).get_usage()

        return [usage.character.count,usage.character.limit]
