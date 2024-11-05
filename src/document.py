from collections import Counter

class Document:

    def __init__(self, sequence_list, document_name=None, document_info_dict=None):
        self.document_name = document_name
        self.num_sequences = 0
        self.sequence_list = []

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

    def update_type_counts(self):
        # Create the type_index_dict from the Counter keys
        self.type_index_dict = {token: idx for idx, token in enumerate(self.type_freq_dict.keys())}
        self.num_types = len(self.type_index_dict)

        # Create the type_list from the keys of the Counter
        self.type_list = list(self.type_freq_dict.keys())

    def add_sequence_list(self, sequence_list):
        # Flatten sequence_list and count frequencies
        flat_sequence = [token for sequence in sequence_list for token in sequence]
        self.num_tokens += len(flat_sequence)

        # Update token frequencies
        self.type_freq_dict.update(flat_sequence)

        # Add sequences and count the total number of sequences
        self.sequence_list.extend(sequence_list)
        self.num_sequences += len(sequence_list)

        self.update_type_counts()


