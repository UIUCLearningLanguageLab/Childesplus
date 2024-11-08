import os
import json
import pickle
from . import corpus
from . import process_childesXML
from . import tokenize

class Childes(corpus.Corpus):

    def __init__(self, params=None):
        super().__init__()
        if params is None:
            self.params = {}
        else:
            self.params = params
        self.params['add_punctuation'] = True

        ## TODO implement subsetting by age, speaker, sex of speaker, language, document, corpus
        ## TODO implement importing phonological, morphological, and syntactic codings where available
        ## TODO implement making sure empty columns are filled by external data if it is available on CHILDES
        ## TODO implement custom tokenization
        ## TODO implement replacement dictionary
        ## TODO implement sorting and batching documents by criteria like age

    def add_childes_xml(self, input_directory):
        namespace = {'ns': 'http://www.talkbank.org/ns/talkbank'}
        file_path_list = process_childesXML.get_document_file_path_list(input_directory)

        num_documents = len(file_path_list)

        for i, file_path in enumerate(file_path_list):
            transcript_name = os.path.splitext(os.path.relpath(file_path, input_directory))[0]
            participants, target_child_age, utterance_dict_list = process_childesXML.process_xml_file(file_path,
                                                                                                      namespace)

            if i % 100 == 0:
                print(f"Adding document {transcript_name} ({i + 1}/{num_documents})")

            utterance_dict_list = process_childesXML.combine_quotation_utterances(utterance_dict_list, "forward")
            utterance_dict_list = process_childesXML.combine_quotation_utterances(utterance_dict_list, "backward")

            utterance_dict_list = self.process_utterance_dict_list(utterance_dict_list)
            document_info_dict = {"participants": participants,
                                  "target_child_age": target_child_age,
                                  "utterance_dict_list": utterance_dict_list}

            sequence_list = [item["token_list"] for item in utterance_dict_list]

            self.add_document(sequence_list, document_name=transcript_name, document_info_dict=document_info_dict)

    def process_utterance_dict_list(self, utterance_dict_list):
        for utterance_dict in utterance_dict_list:
            utterance_text = utterance_dict['utterance_text']
            utterance_text = utterance_text.lower()
            token_list = tokenize.tokenize(utterance_text)

            if 'add_punctuation' in self.params:
                if self.params['add_punctuation']:
                    if len(token_list) > 0:
                        punctuation_string = process_childesXML.get_punctuation(utterance_dict['terminator_type'])
                        token_list.append(punctuation_string)

            utterance_dict['token_list'] = token_list
        return utterance_dict_list

