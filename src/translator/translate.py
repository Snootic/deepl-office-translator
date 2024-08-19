import deepl
import pandas as pd
from docx import Document

class Translate:
    def __init__(self, api_key: str) -> None:
        self.translator = deepl.Translator(api_key)

    def translate_word(self, doc_path: str, source_lang: str = None, target_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        doc = Document(doc_path)
        
        saving_iterations = 0
        
        for paragraph in doc.paragraphs:
            if paragraph.text and paragraph.text.strip() !="":
                try:
                    original_run = paragraph.runs[0]
                except Exception as e:
                    print(e)

                translated_text = self.translate_text(paragraph.text, source_lang, target_lang, glossary, **kwargs)
                
                paragraph.text = translated_text
                
                for run in paragraph.runs:
                    run.style = original_run.style
                    run.bold = original_run.bold
                    run.italic = original_run.italic
                    run.underline = original_run.underline
                    run.font.size = original_run.font.size
                    run.font.color.rgb = original_run.font.color.rgb
                    run.font.name = original_run.font.name

                saving_iterations +=1

                if saving_iterations > 5:
                    doc.save(doc_path)
                    saving_iterations = 0
    
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