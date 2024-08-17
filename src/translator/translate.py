import deepl
import pandas as pd
from docx import Document

class Translate:
    def __init__(self, api_key: str) -> None:
        self.translator = deepl.Translator(api_key)

    def translate_word(self, doc_path: str, source_lang: str = None, target_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        doc = Document(doc_path)
        
        for paragraph in doc.paragraphs:
            original_text = paragraph.text
            translated_text = self.translate_text(original_text, source_lang, target_lang, glossary, **kwargs)
            
            try:
                paragraph.clear()
                paragraph.add_run(translated_text)
                
                for run in paragraph.runs:
                    new_run = paragraph.add_run(translated_text)
                    new_run.bold = run.bold
                    new_run.italic = run.italic
                    new_run.underline = run.underline
                    new_run.font.size = run.font.size
                    new_run.font.color.rgb = run.font.color.rgb

                print(original_text)
                print(translated_text)
                
            except Exception as e:
                print(f"Error: {e}")
                
            doc.save(doc_path)
    
    def translate_excel(self, spreadsheet_path: str, source_column:str, target_column:str, source_lang: str = None, target_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        df = pd.read_excel(spreadsheet_path)
        
        df[target_column] = df[source_column].apply(lambda x: self.translate_text(x, source_lang=source_lang, target_lang=target_lang, glossary=glossary, **kwargs))

        df.to_excel('translated_spreadsheet.xlsx', index=False)  
           
    def translate_text(self, text: str, source_lang: str = None, target_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        try:
            result = self.translator.translate_text(text, source_lang=source_lang, target_lang=target_lang, glossary=glossary, **kwargs)
            return result.text
        except Exception as e:
            print(f"Translation Error: {e}")
            print(f"Failed Text: {text}")
            return text

if __name__ == "__main__":
    translate = Translate("API-KEY")
    translate.translate_word("teste.docx","EN","PT-BR")