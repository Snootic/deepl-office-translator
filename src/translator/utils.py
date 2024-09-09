import json
import deepl
import openai
from openai import OpenAI
import sys

class DeeplAccount():
    def __init__(self,api_key:str) -> None:
        self.API_KEY = api_key

    def check_usage(self) -> list:
        usage = deepl.Translator(self.API_KEY).get_usage()
        
        usage_dict = {}
        
        if usage.character.valid:
            usage_dict["used_characters"] = usage.character.count
            usage_dict["characters_limit"] = usage.character.limit
            usage_dict["characters_limit_reached"] = usage.character.limit_reached
        
        if usage.document.valid:
            usage_dict["used_documents"] = usage.document.count
            usage_dict["documents_limit"] = usage.document.limit
            usage_dict["documents_limit_reached"] = usage.document.limit_reached

        return usage_dict
    
    def get_languages(self,type: str):
        """
            type is either source or target
        """
        
        languages_raw = []
        
        if type == "source":
            languages_raw = deepl.Translator(self.API_KEY).get_source_languages()
            
        if type == "target":
            languages_raw = deepl.Translator(self.API_KEY).get_target_languages()
        
        languages = [language.__dict__ for language in languages_raw]
            
        return languages

class GPTAccount():
    def __init__(self,api_key:str) -> None:
        self.API_KEY = api_key
        self.client = OpenAI(api_key=api_key)
        
    def models(self):
        gpt_models = self.client.models.list()
        
        models = []
        for model in gpt_models:
            if model.id.__contains__("gpt-4o"):
                models.append(model.id)

        gpt_models = {"gpt_models": models}
                
        return gpt_models
    
    def account_billing():
        #TODO
        pass

if __name__ == "__main__": 
    help = """
        you must pass an argument to this program!
        
        example: program.exe key=api_key method=check_usage args=arg1,arg2
        
        available commands:
        "help": show this
        "tool": the tool you want to use. It can be either gpt or deepl for now
        "key": the account api key
        "method": the function you want to access
        "args": the function arguments you want to pass if available
    """
    available_args = ["help","tool","key","method","args"]
    args = {}
    call_arguments = []
    for arg in sys.argv:
        try:
            arg = arg.split("=",1)
            if arg[0] != sys.argv[0] and arg[0] not in available_args:
                raise ValueError
            if arg[0] == "args":
                call_arguments = arg[1].split(",")
                continue
            args[arg[0]] = arg[1]
        except ValueError:
            print("Invalid argument")
        except IndexError:
            if arg[0] == sys.argv[0]:
                pass
            else:
                print("invalid argument or missing parameter")
            
    if len(sys.argv) < 2 or "help" in sys.argv:
        print(help)
    
    else:
        try:
            if args["tool"] == "gpt":
                account = GPTAccount(args["key"])
            elif args["tool"] == "deepl":
                account = DeeplAccount(args["key"])
            else:
                raise(KeyError("tool is invalid"))
            result = getattr(account,args["method"])(*call_arguments)
            # print(result)
            if type(result) != str:
                result = json.dumps(obj=result,skipkeys=True, default=lambda o: '<not serializable>',indent=2)

            print(result)
            
        except deepl.DeepLException as d:
            print(f"Invalid API key: {d}")
        except KeyError as k:
            print(f"something wrong with parameter: {k}")
        # except TypeError as t:
        #     print("TypeError: ",t)