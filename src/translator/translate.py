import json
import deepl
import pandas as pd
from docx import Document
from pptx import Presentation
from openai import OpenAI
from io import BytesIO
import sys

class Translate:
    # All returns must be json parsable
    
    def __init__(self, model: str, api_key: str, **kwargs) -> None:
        self.model = model
        if model.__contains__("gpt"):
            self.client = OpenAI(api_key=api_key, **kwargs)
        else:
            self.translator = deepl.Translator(api_key)

    def translate_pptx(self, presentation_path: str, output_path: str, target_lang: str, source_lang: str = None, glossary: deepl.GlossaryInfo | str = None, **kwargs):
        prs = Presentation(presentation_path)

        saving_iterations = 0
        # print(len(prs.slides))
        
        word_bank = {}
        try:
            for slide in prs.slides:
                for shape in slide.shapes:
                    
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            for run in paragraph.runs:
                                original_text = run.text.rstrip()
                                
                                if not original_text.strip() or original_text.isdigit():
                                    continue
                                
                                if word_bank.get(original_text):
                                    run.text = word_bank[original_text]
                                    continue
                                        
                                translated_text = self.translate_text(original_text, target_lang, source_lang, **kwargs)
                                
                                # translated_text = "isso é um parágrafo"
                                
                                word_bank[original_text] = translated_text
                                    
                                run.text = translated_text
                                    
                    if shape.has_table:
                        table = shape.table 
                        table_data = []
                        for row in table.rows:
                            for cell in row.cells:
                                original_text = cell.text.rstrip()
                                
                                if not original_text.strip() or original_text.isdigit():
                                    continue
                                
                                if word_bank.get(original_text):
                                    cell.text = word_bank[original_text]
                                    continue
                                
                                translated_text = self.translate_text(original_text, target_lang, source_lang, **kwargs)
                                
                                # translated_text = "isso é uma célula de tabela"
                                
                                word_bank[original_text] = translated_text
                                    
                                cell.text = translated_text
                        
                    if shape.has_chart:
                        try:
                            blob_stream = BytesIO(shape.chart._workbook.xlsx_part.blob)
                            sheets = pd.ExcelFile(blob_stream).sheet_names
                            df = pd.read_excel(blob_stream)
                            columns = df.columns.tolist()
                            
                            for index, column in enumerate(columns):
                                if not column.strip() or column.isdigit():
                                    continue
                                
                                if word_bank.get(column):
                                    columns[index] = word_bank[column]
                                    continue
                                
                                new_column = self.translate_text(column, target_lang, source_lang, **kwargs)
                                
                                # new_column = "isso é uma coluna"
                                
                                word_bank[column] = new_column
                                
                                columns[index] = new_column
                                
                            row_data = df.values.tolist()
                            for row in row_data:
                                for index, data in enumerate(row):
                                    if isinstance(data, (int,float)) or not data.strip():
                                        continue
                                    
                                    if word_bank.get(data):
                                        row[index] = word_bank[data]
                                        continue
                                    
                                    row[index] = self.translate_text(data, target_lang, source_lang, **kwargs)
                                    
                                    # row[index] = "isso é uma linha"
                                
                                    word_bank[data] = row[index]
                            
                            new_df = pd.DataFrame(data=row_data,columns=columns)
                            
                            blob = BytesIO()
                            new_df.to_excel(blob,index=False, sheet_name=sheets[0], engine='xlsxwriter')
                            blob.seek(0)
                            
                            blob_data = blob.getvalue()
                            
                            shape.chart._workbook.xlsx_part.blob = blob_data
                            
                        except Exception as e:
                            continue
                                            
                saving_iterations+=1
        except:
            prs.save(output_path)

        prs.save(output_path)

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
            raise error

    def translate_word_preserve_format(self,doc_path: str, output_path: str, target_lang: str, source_lang: str = None, glossary: deepl.GlossaryInfo | str = None, **kwargs):
        doc = Document(doc_path)

        def translate_paragraph(element):
            saving_iterations = 0
            for paragraph in element.paragraphs:
                if paragraph.text and paragraph.text.strip() !="":
                    try:
                        original_run = paragraph.runs[0]
                    except:
                        pass

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
                        doc.save(output_path)
                        saving_iterations = 0

        def translate_tables():
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        translate_paragraph(cell)

        translate_paragraph(doc)
        translate_tables()
        
        doc.save(output_path)

    def translate_excel(self, spreadsheet_path: str, output_path: str, source_column:str, target_column:str, target_lang: str,  source_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        df = pd.read_excel(spreadsheet_path)
        
        df[target_column] = df[source_column].apply(lambda x: self.translate_text(x, source_lang=source_lang, target_lang=target_lang, glossary=glossary, **kwargs))

        df.to_excel(output_path, index=False)  
           
    def deepl_translate_text(self, text: str, source_lang: str = None, target_lang: str = None, glossary: deepl.GlossaryInfo = None, **kwargs):
        try:
            result = self.translator.translate_text(text, source_lang=source_lang, target_lang=target_lang, glossary=glossary, **kwargs)
            return result.text
        except deepl.DeepLException as d:
            raise d
        except:
            return text

    def gpt_translate_text(self, text: str, target_language:str, source_language:str, context: str | None = None):
        
        if context:
            input = context + "(text below): " + text
        else:
            input = text
        completion = self.client.chat.completions.create(
            model=self.model,
            
            messages=[
                {
                    "role": "system", 
                    "content": f"""You are the best poliglot translator in the world, you translate like no one. 
                        You adapt all language expressions from all diferent cultures and countries, and make all text sound like natural to native speakers. 
                        You preserve the format of the text, leaving it the way it was written, transmitting the feeling and meaning of the original text to the translated one.
                        Translate the text below to {target_language} from {source_language}. Return only the translated text"""
                },
                {
                    "role": "user",
                    "content": input
                }
            ]
        )
        
        return completion.choices[0].message.content
    
    def translate_text(self, *args, **kwargs):
        if self.model.__contains__("gpt"):
            return self.gpt_translate_text(*args,**kwargs)
        return self.deepl_translate_text(*args,**kwargs)
    
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
    available_args = ["help","model","key","method","args"]
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
            account = Translate(args["model"],args["key"])
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
        except Exception as e:
            print("Ocorreu um erro: ", e)