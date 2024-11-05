import pickle
from collections import Counter
from . import document

class Corpus:

    def __init__(self):

        self.num_documents = 0
        self.document_list = []

        self.num_sequences = 0
        self.num_tokens = 0

        self.num_types = 0
        self.type_list = []
        self.type_index_dict = {}
        self.type_freq_dict = Counter()

        self.vocab_list = None
        self.vocab_index_dict = None
        self.vocab_size = None
        self.unknown_token = None

    def add_document(self, sequence_list, document_name=None, document_info_dict=None):
        if document_info_dict is None:
            document_info_dict = {}

        new_document = document.Document(sequence_list,
                                         document_name=document_name,
                                         document_info_dict=document_info_dict)
        self.num_documents += 1
        self.document_list.append(new_document)
        self.type_freq_dict += new_document.type_freq_dict
        self.type_list = list(self.type_freq_dict.keys())
        self.type_index_dict = {key: idx for idx, key in enumerate(self.type_list)}
        self.num_types += new_document.num_types
        self.num_tokens += new_document.num_tokens
        self.num_sequences += new_document.num_sequences

    def set_unknown_token(self, unknown_token="<UNK>"):
        while self.unknown_token is None:
            if unknown_token in self.type_freq_dict:
                unknown_token = "<" + unknown_token + ">"
            else:
                self.unknown_token = unknown_token

    def create_vocab(self, vocab_size=None, include_list=(), exclude_list=(), include_unknown=True):
        print(f"Creating vocab list of size {vocab_size} and include_unknown={include_unknown}")

        # create the empty vocab list structures
        self.vocab_list = []
        self.vocab_index_dict = {}
        self.vocab_size = 0
        missing_word_list = []

        # if vocab_size is None, set it to the size of the freq_dict so all words are used
        # account for the unknown token if it will be included
        if vocab_size is None:
            if include_unknown:
                vocab_size = len(self.type_freq_dict) + 1
            else:
                vocab_size = len(self.type_freq_dict)

        # add unknown token to vocab
        if include_unknown:
            self.set_unknown_token()
            self.add_token_to_vocab(self.unknown_token)

        # get a filtered copy of the freq_dict that does not include any excluded words
        filtered_freq_dict = self.type_freq_dict.copy()
        if exclude_list:
            for token in exclude_list:
                filtered_freq_dict.pop(token, None)  # pop removes safely without checking

        if len(filtered_freq_dict) == 0:
            raise ValueError("ERROR making vocab list: After exclusion list there are no words in the corpus")

        # add words from the include list to the vocab data structures as long as they are in the filtered freq_dict
        for token in include_list:
            if token in filtered_freq_dict:
                self.add_token_to_vocab(token)
                filtered_freq_dict.pop(token, None)
            else:
                missing_word_list.append(token)

        # Add items from the counter to vocab_list it is not vocab_size
        if vocab_size > self.vocab_size:

            # Sort the counter by frequency (count), then by word
            sorted_tokens = sorted(filtered_freq_dict, key=lambda new_word: (-filtered_freq_dict[new_word], new_word))

            # Add words to vocab_list in frequency order until it reaches size m
            for token in sorted_tokens:
                if self.vocab_size >= vocab_size:
                    break
                if token not in self.vocab_index_dict:
                    self.add_token_to_vocab(token)

        return missing_word_list

    def add_token_to_vocab(self, token):
        self.vocab_list.append(token)
        self.vocab_index_dict[token] = self.vocab_size
        self.vocab_size += 1

    @staticmethod
    def tokenize(text_string):
        token_list = text_string.split()
        return token_list

    def save_pkl(self, file_path):
        print(f"Saving corpus to pkl {file_path}")
        """Save the instance to a file."""
        with open(file_path+'.pkl', 'wb') as file:
            pickle.dump(self, file)

    @classmethod
    def load_pkl(cls, file_path):
        with open(file_path, 'rb') as file:
            return pickle.load(file)

