import os
import math
import random
import sys
import csv
import time


sys.path.append('..')

from base.data_loader import BaseDataLoader
from base.globals import *
from base.partition import *

# if download with script in data folder 
# data_dir shoule be '../../../../data//fednlp/text_classification/AGNews'


class DataLoader(BaseDataLoader):
    def __init__(self, data_path, **kwargs):
        super().__init__(data_path, **kwargs)
        allowed_keys = {"source_padding", "target_padding", "source_max_sequence_length",
                        "target_max_sequence_length", "vocab_path", "initialize"}
        self.__dict__.update((key, False) for key in allowed_keys)
        self.__dict__.update((key, value) for key, value in kwargs.items() if key in allowed_keys)
        self.source_sequence_length = []
        self.target_sequence_length = []
        self.title = []

        if self.tokenized:
            self.vocab = dict()
            self.label_vocab = {'1':'World','2':'Sports','3':'Sports','4':'Sci/Tech'}
            if self.initialize:
                self.vocab[SOS_TOKEN] = len(self.vocab)
                self.vocab[EOS_TOKEN] = len(self.vocab)            
        if self.source_padding or self.target_padding:
            self.vocab[PAD_TOKEN] = len(self.vocab)
            self.label_vocab[PAD_TOKEN] = len(self.vocab)

    def tokenize(self,document):
        # Create a blank Tokenizer with just the English vocab
        tokens = [str(token) for token in spacy_tokenizer.en_tokenizer(document)]
        for i in list(tokens):
            if i not in self.vocab:
                self.vocab[i] = len(self.vocab)
        return tokens
    
    def process_data(self,file_path):
        with open(file_path,"r",newline='') as csvfile:
            data = csv.reader(csvfile,delimiter=',')
            source = ""
            target = ""
            for line in data:
                target = self.label_vocab[line[0]]
                source = line[2].replace('\\','')
                self.title.append(line[1])
                source_tokens = self.tokenize(source)
                self.X.append(source_tokens)
                self.Y.append([target])
                self.target_sequence_length.append(1)
                self.source_sequence_length.append(len(source_tokens))
        return max(self.source_sequence_length), 1     
                

    def data_loader(self):
        result = dict()
        max_source_length , max_target_length = self.process_data(self.data_path)

        self.padding_data(self.X, max_source_length,self.initialize)


        
        
        result['X'] = self.X
        result['Y'] = self.Y
        result['vocab'] = self.vocab
        result['label_vocab'] = self.label_vocab
        result['source_sequence_length'] = self.source_sequence_length
        result['target_sequence_length'] = self.target_sequence_length
        result['max_source_length'] = max_source_length

        return result


if __name__ == "__main__":
    train_file_path = '../../../../data//fednlp/text_classification/AGNews/train.csv'
    data_loader = DataLoader(train_file_path, tokenized=True, source_padding=True, target_padding=True)
    result = data_loader.data_loader()
    print(result['Y'])    
