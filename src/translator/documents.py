from docx import Document
from pptx import Presentation
import pandas as pd
from typing import Union, IO
import tiktoken
import os
import json
import sys

class File:
    def __init__(self) -> None:
        pass
    
    def load_document(self, file: Union[str, IO[bytes]] = None):
        if isinstance(file, str):
            ext = os.path.splitext(file)[1].lower()
        else:
            ext = os.path.splitext(file.name)[1].lower()

        if ext == ".docx":
            return self.load_word(file)
        elif ext == ".xlsx":
            return self.load_excel(file)
        elif ext == ".pptx":
            return self.load_pptx(file)
        else:
            raise ValueError("Tipo de arquivo não suportado. Por favor, insira um arquivo .docx, .xlsx ou .pptx.")

    def load_excel(self, file: str | IO[bytes ]= None):
        pass
    
    def load_pptx(self, file: str | IO[bytes ]= None):
        try:
            prs = Presentation(file)
        except Exception as e:
            raise(e)

        properties_dir = dir(prs.core_properties)

        properties_keys = [k for k in properties_dir if not k.startswith("_")]
        
        properties = {}
        for key in properties_keys:
            properties[key] = prs.core_properties.__getattribute__(key)

        properties["slide_count"] = len(prs.slides)

        tokens = []
        final_text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame:
                    final_text += shape.text
                    pretokens = self.tokenize(shape.text)
                    for token in pretokens:
                        tokens.append(token)
                    
        properties["word_count"] = len(final_text.split(" "))

        properties["tokens"] = tokens

        properties["tokens_count"] = len(tokens)

        return properties

    def load_word(self, file: str | IO[bytes ]= None):
        try:
            file = Document(file)
        except Exception as e:
            raise(e)

        properties_dir = dir(file.core_properties)
        
        properties_keys = [k for k in properties_dir if not k.startswith("_")]
        
        properties = {}
        for key in properties_keys:
            properties[key] = file.core_properties.__getattribute__(key)

        paragraphs_text = ""
        tokens = []
        for paragraph in file.paragraphs:
            paragraphs_text += paragraph.text
            pretokens = self.tokenize(paragraph.text)
            for token in pretokens:
                tokens.append(token)

        properties["word_count"] = len(paragraphs_text.split(" "))

        properties["tokens"] = tokens

        properties["tokens_count"] = len(tokens)
        
        return properties
    
    def tokenize(self,text):
        enc = tiktoken.encoding_for_model("gpt-4o")
        tokens = enc.encode(text)

        return tokens
    

file = File()