import torch
from torch.utils.data import Dataset


class BasicDataset(Dataset):

    def __init__(self):

        self.x_label_list = None
        self.x_index_dict = None
        self.num_x = None
        self.x_shape = None

        self.y_label_list = None
        self.y_index_dict = None
        self.num_y = None
        self.y_shape = None

        self.x_list = None  # the 1D list of indexes
        self.y_list = None

    def __len__(self):
        return len(self.x_list)

    def __getitem__(self, idx):
        x = torch.tensor(self.x_list[idx], dtype=torch.long)
        y = torch.tensor(self.y_list[idx], dtype=torch.long)
        return x, y

    @staticmethod
    def create_sequence_lists(index_list, sequence_length, pad_index):
        if sequence_length == 2:
            # Each sequence is a single element from the index_list
            return [[index] for index in index_list]
        else:
            # Original logic for longer sequences
            padded_list = [pad_index] * (sequence_length - 2) + index_list
            sequence_lists = []
            for i in range(len(padded_list) + 1):
                if i + sequence_length <= len(padded_list):
                    sequence = padded_list[i:i + sequence_length]
                    sequence_lists.append(sequence)
            return sequence_lists

    @staticmethod
    def create_batches(sequence_list, batch_size, sequence_length, pad_index):
        x_batches = []
        y_batches = []
        y_window_batches = []
        current_batch_x = []
        current_batch_y = []
        current_batch_y_window = []

        if sequence_length == 1:
            for i in range(len(sequence_list) - 1):
                current_batch_x.append(sequence_list[i])
                current_batch_y.append(sequence_list[i + 1])
                current_batch_y_window.append(sequence_list[i + 1])

                if len(current_batch_x) == batch_size:
                    x_batches.append(current_batch_x)
                    y_batches.append(current_batch_y)
                    y_window_batches.append(current_batch_y)
                    current_batch_x = []
                    current_batch_y = []
                    current_batch_y_window = []
        else:
            for sequence in sequence_list:
                current_batch_x.append(sequence[:-1])  # Take all but the last element
                current_batch_y.append([sequence[-1]])  # Take the last element
                current_batch_y_window.append(sequence[1:])
                if len(current_batch_x) == batch_size:
                    x_batches.append(current_batch_x)
                    y_batches.append(current_batch_y)
                    y_window_batches.append(current_batch_y_window)
                    current_batch_x = []
                    current_batch_y = []
                    current_batch_y_window = []

            # Pad the last batch if necessary. this last bit is missing the completion for y_window_batches
            if current_batch_x:
                while len(current_batch_x) < batch_size:
                    current_batch_x.append([pad_index] * sequence_length)
                    current_batch_y.append([pad_index])
                    current_batch_y_window.append([pad_index] * sequence_length)

                x_batches.append(current_batch_x)
                y_batches.append(current_batch_y)
                y_window_batches.append(current_batch_y_window)

        return x_batches, y_batches, y_window_batches

    def create_batched_sequence_lists(self, document_list, window_size, window_direction, batch_size, sequence_length,
                                      device):
        corpus_token_list = self.flatten_corpus_lists(document_list)
        pad_index = 0
        window_size = window_size
        window_direction = window_direction
        self.x_list, self.y_list, self.index_list = self.create_index_list(corpus_token_list,
                                                                           self.vocab_index_dict,
                                                                           self.unknown_token,
                                                                           window_size=window_size,
                                                                           window_direction=window_direction)
        if window_size == 1:
            sequence_list = self.create_sequence_lists(self.index_list, sequence_length + 1, pad_index=pad_index)

            x_batches, y_batches, y_window_batches = self.create_batches(sequence_list, batch_size, sequence_length,
                                                                         pad_index)
        else:
            x_batches = [[self.x_list[i:i + batch_size]] for i in range(0, len(self.x_list), batch_size)]
            y_batches = [[self.y_list[i:i + batch_size]] for i in range(0, len(self.y_list), batch_size)]
            y_window_batches = []

        x_batches = [torch.tensor(x_batch, dtype=torch.long).to(device) for x_batch in x_batches]
        y_batches = [torch.tensor(y_batch, dtype=torch.long).to(device) for y_batch in y_batches]
        y_window_batches = [torch.tensor(y_window_batch, dtype=torch.long).to(device) for y_window_batch in
                            y_window_batches]

        return x_batches, y_batches, y_window_batches