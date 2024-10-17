from collections import Counter

class Document:

    def __init__(self, document_name):
        self.document_name = document_name
        self.num_sequences = 0
        self.sequence_list = []

        self.num_tokens = 0

        self.vocab_size = 0
        self.vocab_list = []
        self.vocab_index_dict = {}
        self.vocab_freq_dict = Counter()

    def add_sequence_list(self, sequence_list):
        for sequence in sequence_list:
            self.sequence_list.append(sequence)
            self.num_sequences += 1
            self.num_tokens += len(sequence)

            for token in sequence:
                if token not in self.vocab_index_dict:
                    self.vocab_index_dict[token] = self.vocab_size
                    self.vocab_size += 1
                    self.vocab_list.append(token)

                # Use Counter to handle frequency counting
                self.vocab_freq_dict[token] += 1
