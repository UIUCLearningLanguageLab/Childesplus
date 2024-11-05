from src.basic_dataset import Dataset


class LMDataset(Dataset):

    def __init__(self):
        super().__init__()

        self.vocab_size = None
        self.vocab_list = None
        self.vocab_index_dict = None
        self.vocab_freq_dict = None
        self.unknown_token = None

    def create_index_list(self, flattened_list, vocab_index_dict, unknown_token, window_size=None,
                          window_direction=None):
        index_list = self.create_simple_index_list(flattened_list, vocab_index_dict, unknown_token)
        if window_size is not None:
            x, y = self.create_windowed_index_list(index_list, window_size, window_direction)
        else:
            x = index_list[:-1]
            y = index_list[1:]
        return x, y, index_list

    def flatten_corpus_lists(self, nested_list):
        # take an embedded list of whatever depth of embedding, and flatten into a single list
        flat_list = []
        for element in nested_list:
            if isinstance(element, list):
                # If the element is a list, extend flat_list with the flattened element
                flat_list.extend(self.flatten_corpus_lists(element))
            else:
                # If the element is not a list, add it to flat_list
                flat_list.append(element)
        return flat_list

    @staticmethod
    def create_simple_index_list(flattened_list, vocab_index_dict, unknown_token):
        index_list = []
        for token in flattened_list:
            if token in vocab_index_dict:
                current_index = vocab_index_dict[token]
            else:
                current_index = vocab_index_dict[unknown_token]

            index_list.append(current_index)
        return index_list

    @staticmethod
    def create_windowed_index_list(index_list, window_size, direction='both', pad_index=0):
        if window_size == 0:
            raise ValueError("Window size cannot be 0, must be None or positive integer")
        # if direction == 'both':
        #     padded_index_list = [pad_index] * (window_size/2) + index_list
        if direction == 'backward':
            padded_index_list = [pad_index] * window_size + index_list
        else:
            padded_index_list = index_list + [pad_index] * window_size
        x = []
        y = []
        for i in range(len(padded_index_list)):
            for j in range(1, window_size + 1):
                # Check if the index is within the bounds of the list
                if direction == 'both':
                    if i - j >= 0:
                        x.append(padded_index_list[i])
                        y.append(padded_index_list[i - j])
                    if i + j < len(padded_index_list):
                        x.append(padded_index_list[i])
                        y.append(padded_index_list[i + j])
                elif direction == 'forward':
                    if i + window_size < len(padded_index_list):
                        x.append(padded_index_list[i])
                        y.append(padded_index_list[i + j])
                else:
                    if i < len(padded_index_list) - window_size:
                        x.append(padded_index_list[i + j - 1])
                        y.append(padded_index_list[i + window_size])
        return x, y