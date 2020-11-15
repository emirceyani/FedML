import os
import math
import random
from random import shuffle
import sys
import csv
import time


sys.path.append('..')

from base.data_loader import BaseDataLoader
from base.globals import *
from base.partition import *

# if download with script in data folder 
# data_dir shoule be '../../../../data//fednlp/text_classification/SST-2/stanfordSentimentTreebank'

# class DataLoader(BaseDataLoader):
#     def __init__(self, data_path, sentence_index, label_file, partition, **kwargs):
#         super().__init__(data_path, partition, **kwargs)
#         allowed_keys = {"source_padding", "target_padding", "tokenized", "source_max_sequence_length",
#                         "target_max_sequence_length", "vocab_path", "initialize"}
#         self.__dict__.update((key, False) for key in allowed_keys)
#         self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)
#         self.source_sequence_length = []
#         self.target_sequence_length = []
#         self.sentence_index = sentence_index
#         self.label_file = label_file
#         self.attributes = dict()
#         self.attributes['inputs'] = []
#         self.label_vocab = {1:"very",2:"negative",3:"neutral",4:"positive"}
#         self.label_dict = dict()
#
#
#         if self.tokenized:
#             self.vocab = dict()
#             if self.initialize:
#                 self.vocab[SOS_TOKEN] = len(self.vocab)
#                 self.vocab[EOS_TOKEN] = len(self.vocab)
#         if self.source_padding or self.target_padding:
#             self.vocab[PAD_TOKEN] = len(self.vocab)
#             self.label_vocab[PAD_TOKEN] = len(self.vocab)
#
#     def tokenize(self,document):
#         # Create a blank Tokenizer with just the English vocab
#         tokens = [str(token) for token in spacy_tokenizer.en_tokenizer(document)]
#
#         for i in list(tokens):
#             if i not in self.vocab:
#                 self.vocab[i] = len(self.vocab)
#
#         return tokens
#
#     def label_level(self,label):
#         label = float(label)
#         if label >= 0.0 and label <= 0.2:
#             return "very negative"
#         elif label > 0.2 and label <= 0.4:
#             return "negative"
#         elif label > 0.4 and label <= 0.6:
#             return "neutral"
#         elif label > 0.6 and label <= 0.8:
#             return "positive"
#         else:
#             return "very positive"
#
#     def process_data(self,client_idx=None):
#         cnt = 0
#         max_source_length = -1
#
#         with open(self.label_file) as f2:
#             for label_line in f2:
#                 label = label_line.split('|')
#                 self.label_dict[label[0].strip()] = label[1]
#
#
#         for i in self.sentence_index:
#             if client_idx is not None and client_idx != self.attributes["inputs"][cnt]:
#                 cnt+=1
#                 continue
#             data = i.split('|')
#
#             if self.tokenized:
#                 tokens = self.tokenize(data[0].strip())
#                 self.X.append(tokens)
#             else:
#                 tokens = data[0].strip()
#                 self.X.append([tokens])
#
#             self.source_sequence_length.append(len(tokens))
#             max_source_length = max(len(tokens),max_source_length)
#             self.target_sequence_length.append(1)
#             self.Y.append([self.label_level(self.label_dict[data[1].strip()])])
#
#
#         return max_source_length, 1
#
#
#     def data_loader(self,client_idx=None):
#         result = dict()
#         if client_idx is not None:
#             max_source_length , max_target_length = self.process_data(client_idx)
#         else:
#             max_source_length , max_target_length = self.process_data()
#
#         if callable(self.partition):
#             self.attributes = self.partition(self.X, self.Y)
#         else:
#             self.attributes = self.process_attributes()
#
#         if self.source_padding:
#             self.padding_data(self.X, max_source_length, self.initialize)
#
#         if self.tokenized:
#             result['vocab'] = self.vocab
#
#
#         result['X'] = self.X
#         result['Y'] = self.Y
#         result['label_vocab'] = self.label_vocab
#         result['attributes'] = self.attributes
#         result['source_sequence_length'] = self.source_sequence_length
#         result['target_sequence_length'] = self.target_sequence_length
#         result['source_max_sequence_length'] = max_source_length
#         result['target_max_sequence_length'] = max_target_length
#
#         return result


class DataLoader(BaseDataLoader):
    def __init__(self, data_path):
        super().__init__(data_path)
        self.task_type = "classification"
        self.target_vocab = None
        self.label_file_name = "sentiment_labels.txt"
        self.data_file_name = "dictionary.txt"

    def data_loader(self):
        if len(self.X) == 0 or len(self.Y) == 0 or self.target_vocab is None:
            X, Y = self.process_data(self.data_path)
            self.X, self.Y = X, Y
            self.target_vocab = {key: i for i, key in enumerate(set(Y))}
        return {"X": self.X, "Y": self.Y, "target_vocab": self.target_vocab, "task_type": self.task_type}

    def label_level(self, label):
        label = float(label)
        if label >= 0.0 and label <= 0.2:
            return "very negative"
        elif label > 0.2 and label <= 0.4:
            return "negative"
        elif label > 0.4 and label <= 0.6:
            return "neutral"
        elif label > 0.6 and label <= 0.8:
            return "positive"
        else:
            return "very positive"

    def process_data(self, file_path):
        X = []
        Y = []
        label_dict = dict()
        with open(os.path.join(file_path, self.label_file_name)) as f:
            for label_line in f:
                label = label_line.split('|')
                label_dict[label[0].strip()] = label[1]

        with open(os.path.join(file_path, self.data_file_name)) as f:
            for data_line in f:
                data = data_line.strip().split("|")
                X.append(data[0].strip())
                Y.append(self.label_level(label_dict[data[1].strip()]))
        return X, Y


if __name__ == "__main__":
    import pickle
    data_path = '../../../../data//fednlp/text_classification/SST-2/stanfordSentimentTreebank/'

    train_data_loader = DataLoader(data_path)
    train_result = train_data_loader.data_loader()
    uniform_partition_dict = uniform_partition([train_result["X"], train_result["Y"]])
    # pickle.dump(train_result, open("sst_2_data_loader.pkl", "wb"))
    # pickle.dump({"uniform_partition": uniform_partition_dict}, open("sst_2_partition.pkl", "wb"))
    print("done")