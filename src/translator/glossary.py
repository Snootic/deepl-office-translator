import pandas as pd
import json, deepl
import sys

#todo add method overload

class Glossario():
    def __init__(self, api_key:str) -> None:
        self.API_KEY = api_key
        self.glossario: deepl.GlossaryInfo

    def create_from_excel(self,file_path,file_name,excluded_keys:list = None) -> None:
        df = pd.read_excel(file_path)

        if not excluded_keys:
            excluded_keys = []

        if df.shape[1] != 2:
            raise ValueError("O DataFrame deve ter exatamente duas colunas.")


        dicionario = {}
        for row in df.itertuples(index=False):
            chave, valor = row[0], row[1]
            try:
                chave = chave.rstrip()
                valor = valor.rstrip()
            except Exception as e:
                print(e)
                print(chave,valor)
                
            if (chave not in excluded_keys and 
                valor not in excluded_keys and
                pd.notna(chave) and 
                pd.notna(valor)):
                if chave not in dicionario:
                    dicionario[chave] = valor

        with open(f"{file_name}.json", 'w',encoding='utf-8') as teste:
            json.dump(dicionario, teste, indent=2,ensure_ascii=False)

    def create_glossary(self,glossary_name:str,source_language:str,target_language:str,glossary:dict):
        translator = deepl.Translator(self.API_KEY)

        self.glossary = translator.create_glossary(
            glossary_name,
            source_lang=source_language,
            target_lang=target_language,
            entries=glossary
        )
        return self.glossary
    
    def load_json(self,json_file) -> dict:
        with open(json_file,encoding="utf-8") as json_dict:
            glossary = json.load(json_dict)

        return glossary
    
    def get_glossaries(self):
        translator = deepl.Translator(self.API_KEY)
        
        glossaries = translator.list_glossaries()
        
        result = []
        
        for glossary in glossaries:
            result.append(glossary.__dict__)

        return result

    def delete_glossary(self,glossary:deepl.GlossaryInfo|str):
        return deepl.Translator(self.API_KEY).delete_glossary(glossary=glossary)
    
    def get_glossary_entries(self,glossary:deepl.GlossaryInfo|str):
        return deepl.Translator(self.API_KEY).get_glossary_entries(glossary)
    
    def get_glossary_languages(self):
        glossary_languages = deepl.Translator(self.API_KEY).get_glossary_languages()
        
        languages = []
        
        for glossary_language in glossary_languages:
            languages.append(glossary_language.__dict__)
        
        return languages
    
    def create_glossary_from_csv(self,csv_file_path:str,glossary_name:str,source_language:str,target_language:str):
        translator = deepl.Translator(self.API_KEY)

        with open(csv_file_path,encoding="utf-8") as file:
            csv_file = pd.read_csv(file)

        self.glossary = translator.create_glossary_from_csv(
            name=glossary_name,
            source_lang=source_language,
            target_lang=target_language,
            csv_data=csv_file
        )
        return self.glossary.__dict__

if __name__ == "__main__":
    help = """
        you must pass an argument to this program!
        
        example: program.exe key=api_key method=check_usage args=arg1,arg2
        
        available commands:
        "help": show this
        "key": the account api key
        "method": the function you want to access
        "args": the function arguments you want to pass if available
    """
    available_args = ["help","key","method","args"]
    args = {}
    call_arguments = []
    for arg in sys.argv:
        try:
            arg = arg.split("=")
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
            account = Glossario(args["key"])
            result = getattr(account,args["method"])(*call_arguments)
            if type(result) != str:
                result = json.dumps(obj=result,skipkeys=True, default=lambda o: '<not serializable>',indent=2)

            print(result)
            
        except deepl.DeepLException as d:
            print(f"Invalid API key: {d}")
        except KeyError as k:
            print(f"missing parameter {k}")
        except TypeError as t:
            print(t)