import copy
import random
import corpus
import csv
import preprocess


class Childes(corpus.Corpus):

    """
        Imports corpus.Corpus, which has the following attributes:
            self.document_headers

            self.num_documents
            self.document_info_df: required columns: ["name", "num_sequences", "num_types", "num_tokens"]
            self.document_list

            self.num_sequences
            self.num_types
            self.num_tokens
            self.corpus_freq_dict

            self.vocab_list
            self.vocab_index_dict
            self.vocab_size
            self.unknown_token

            self.index_list = None
            self.x_list = None
            self.y_list = None
    """

    def __init__(self):
        super().__init__()

        self.language = None
        self.age_range_tuple = None
        self.sex_list = None
        self.add_punctuation = None
        self.exclude_target_child = None
        self.order = None

        ## TODO implement subsetting the corpus by sex of speaker, target child, language, corpus
        ## TODO implement subsetting by age, adding punctuation, excluding target child self speech
        ## TODO implement importing phonological, morphological, and syntactic codings where available
        ## TODO implement making sure empty columns are filled by external data if it is available on CHILDES

        self.document_info_list = None

    def get_documents_from_csv_file(self, input_path):
        with open('your_file.csv', newline='') as file:

            reader = csv.DictReader(file)
            utterance_dict_list = [row for row in reader]


        document_sequence_list = None
        document_info_dict = None
        current_document_name = None
        document_counter = 0

        for utterance_info in utterance_info_list:
            utterance_document_name = utterance_info[0]
            utterance = utterance_info[1]
            speaker_id = utterance_info[2]
            speaker_name = utterance_info[3]
            speaker_role = utterance_info[4]
            speaker_age_months = int(utterance_info[5])
            speaker_gender = utterance_info[6]
            speaker_language = utterance_info[7]
            start_time_sec = utterance_info[8]
            end_time_sec = utterance_info[9]
            duration_sec = utterance_info[10]
            comments_text = utterance_info[11]
            target_child_age = int(utterance_info[12])

            if utterance_document_name != current_document_name:
                if document_counter > 0:
                    self.add_document(document_sequence_list, tokenized=True, document_info_dict=document_info_dict)

                current_document_name = utterance_document_name
                document_sequence_list = []
                document_info_dict = {}

            self.process_utterance(utterance)



    def process_utterance(self, utterance):
        cleaned_utterance = preprocess.clean_text(utterance)


    @staticmethod
    def tokenize(text_string):
        token_list = text_string.split()
        return token_list

    @staticmethod
    def get_punctuation(utterance_type):
        punctuation_dict = {'declarative': ".",
                            "question": "?",
                            "trail off": ";",
                            "imperative": "!",
                            "imperative_emphatic": "!",
                            "interruption": ":",
                            "self interruption": ";",
                            "quotation next line": ";",
                            "interruption question": "?",
                            "missing CA terminator": ".",
                            "broken for coding": ".",
                            "trail off question": "?",
                            "quotation precedes": ".",
                            "self interruption question": "?",
                            "question exclamation": "?"}
        return punctuation_dict[utterance_type]

    def create_utterance_token_list(self, gloss, utterance_type):
        token_list = self.tokenize(gloss)
        if self.add_punctuation:
            token_list.append(self.get_punctuation(utterance_type))
        return token_list

    def subset_documents(self, utterance_df):

        utterance_df = utterance_df.dropna(subset=['gloss'])

        if self.language is not None:
            utterance_df = utterance_df[utterance_df['language'] == self.language]
        if self.collection_name is not None:
            utterance_df = utterance_df[utterance_df['collection'] == self.collection_name]
        if self.sex_list is not None:
            utterance_df = utterance_df[utterance_df['target_child_sex'].isin(self.sex_list)]

        # TODO TEST THIS
        if self.age_range_tuple is not None:
            utterance_df = utterance_df.dropna(subset=['target_child_age'])
            utterance_df = utterance_df[(utterance_df[
                                             'target_child_age'] >= self.age_range_tuple[0]) & (utterance_df[
                                                                                                    'target_child_age'] <=
                                                                                                self.age_range_tuple[
                                                                                                    1])]

        if self.exclude_target_child:
            utterance_df = utterance_df[utterance_df["speaker_role"] != "Target_Child"]

        utterance_df = utterance_df.sort_values(by=["target_child_age", "transcript_id", "utterance_order"],
                                                ascending=[True, True, True])

        return utterance_df

    def sort_documents_by_age(self, tuple_list):
        if self.order == "age_ordered":
            sorted_tuple_list = sorted(tuple_list, key=lambda x: x[1])
        elif self.order == 'reverse_age_ordered':
            sorted_tuple_list = sorted(tuple_list, key=lambda x: x[1], reverse=True)
        else:
            sorted_tuple_list = copy.deepcopy(tuple_list)
            random.shuffle(sorted_tuple_list)

        return sorted_tuple_list

    def batch_docs_by_age(self, num_batches=10, order="age_ordered"):
        if order == 'reversed':
            self.document_list.reverse()
        elif order == 'shuffled':
            random.shuffle(self.document_list)
        elif order == 'age_ordered':
            pass
        else:
            raise ValueError(f"Unrecognized corpus document order {order}")

        k, m = divmod(len(self.document_list), num_batches)
        self.document_list = [
            self.document_list[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(num_batches)]