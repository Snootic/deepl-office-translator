import json
import deepl
import pandas as pd
from docx import Document
import sys

class Translate:
    def __init__(self, api_key: str) -> None:
        self.translator = deepl.Translator(api_key)

    def translate_doc(self,doc_path: str, target_lang: str, source_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        output_path_list = doc_path.split('.')
        doc_extension = output_path_list[-1]
        output_path_list.pop()
        output_path_list.append(f"Translated {target_lang}")
        output_path_list.append(doc_extension)

        output_path = output_path_list[0]
        output_path_list.pop(0)

        for item in output_path_list:
            output_path += f".{item}"
        try:
            with open(doc_path, "rb") as in_file, open(output_path, "wb") as out_file:
                self.translator.translate_document(
                    in_file,
                    out_file,
                    source_lang=source_lang,
                    target_lang=target_lang,
                    glossary=glossary,
                    **kwargs
                )

        except deepl.DocumentTranslationException as error:
            doc_id = error.document_handle.document_id
            doc_key = error.document_handle.document_key
            print(f"Error after uploading ${error}, id: ${doc_id} key: ${doc_key}")
        except deepl.DeepLException as error:
            print(error)

    def translate_word_preserve_format(self,doc_path: str, target_lang: str, source_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        doc = Document(doc_path)

        def translate_paragraph(element):
            saving_iterations = 0
            for paragraph in element.paragraphs:
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

        def translate_tables():
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        translate_paragraph(cell)

        translate_paragraph(doc)
        translate_tables()
        
        doc.save(doc_path)

    def translate_excel(self, spreadsheet_path: str, source_column:str, target_column:str, target_lang: str,  source_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
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
            account = Translate(args["key"])
            result = getattr(account,args["method"])(*call_arguments)
            # print(result)
            if type(result) != str:
                result = json.dumps(obj=result,skipkeys=True, default=lambda o: '<not serializable>',indent=2)

            print(result)
            
        except deepl.DeepLException as d:
            print(f"Invalid API key: {d}")
        except KeyError as k:
            print(f"missing parameter {k}")
        except TypeError as t:
            print(t)