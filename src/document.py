from collections import Counter

class Document:

    def __init__(self, sequence_list, document_name=None, document_info_dict=None):
        self.document_name = document_name
        self.num_sequences = 0
        self.sequence_list = None

        self.num_tokens = 0
        self.num_types = 0
        self.type_list = []
        self.type_index_dict = {}
        self.type_freq_dict = Counter()

        if document_info_dict is None:
            self.document_info_dict = {}
        else:
            self.document_info_dict = document_info_dict

        self.add_sequence_list(sequence_list)

    def add_sequence_list(self, sequence_list):
        for sequence in sequence_list:
            self.sequence_list.append(sequence)
            self.num_sequences += 1
            self.num_tokens += len(sequence)

            for token in sequence:
                if token not in self.type_index_dict:
                    self.type_index_dict[token] = self.num_types
                    self.num_types += 1
                    self.type_list.append(token)

                # Use Counter to handle frequency counting
                self.type_freq_dict[token] += 1
