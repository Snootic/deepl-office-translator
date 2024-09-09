from docx import Document
from pptx import Presentation
import pandas as pd
from typing import IO
import sys

class File:
    def __init__(self) -> None:
        pass
    
    def load_document(self, file_path: str = None, input_file: IO[bytes] = None):
        if input_file:
            try:
                file = Document(file)
            except Exception as e:
                print(f"an error occured trying to import the file: {e}")
        elif file_path:
            try:
                file = Document(file_path)
            except Exception as e:
                print(f"an error occured trying to import the file: {e}")
        else:
            raise(KeyError("you must input a file!"))
        
        properties_dir = dir(file.core_properties)
        
        properties_keys = [k for k in properties_dir if not k.startswith("_")]
        
        properties = {}
        for key in properties_keys:
            properties[key] = file.core_properties.__getattribute__(key)
            
        return properties
    
    def load_excel(self):
        pass
    
    def load_pptx(self):
        pass
    
    def load_word(self):
        pass
    
if __name__ == "__main__":
    file = File()
    file.load_document("/home/snootic/Downloads/atividade de tarefa-interesse-amizade.docx")