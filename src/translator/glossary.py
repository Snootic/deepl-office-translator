import pandas as pd
import json, deepl

#todo add method overload

class Glossario():
    def __init__(self, api_key:str) -> None:
        self.API_KEY = api_key
        self.glossario: deepl.GlossaryInfo

    def create_json(self,file_path,file_name) -> None:
        df = pd.read_excel(file_path)

        if df.shape[1] != 2:
            raise ValueError("O DataFrame deve ter exatamente duas colunas.")

        valores_excluidos = ["Field Name", "English", "english", "ENGLISH", "Instructions", "Description","Spanish", "SPANISH", "spanish"]

        dicionario = {}
        for row in df.itertuples(index=False):
            chave, valor = row[0], row[1]
            try:
                chave = chave.rstrip()
                valor = valor.rstrip()
            except Exception as e:
                print(e)
                print(chave,valor)
                
            if (chave not in valores_excluidos and 
                valor not in valores_excluidos and
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
    
    def load_json(self,json_file):
        with open(json_file,encoding="utf-8") as json_dict:
            glossary = json.load(json_dict)

        return glossary
    
    def get_glossaries(self):
        translator = deepl.Translator(self.API_KEY)

        return translator.list_glossaries()

    def delete_glossary(self,glossary:deepl.GlossaryInfo):
        return deepl.Translator(self.API_KEY).delete_glossary(glossary=glossary)
    
    def get_glossary_entries(self,glossary:deepl.GlossaryInfo):
        return deepl.Translator(self.API_KEY).get_glossary_entries(glossary)
    
    def get_glossary_languages(self,glossary:deepl.GlossaryInfo):
        return deepl.Translator(self.API_KEY).get_glossary_languages(glossary)
    
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
        return self.glossary

if __name__ == "__main__":
    glossary = Glossario.create_glossary("My_glossary","EN","PT-BR",{"test":"teste","game":"jogo","keyboard":"teclado"})
    print(glossary)