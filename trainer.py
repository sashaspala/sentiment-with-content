from nltk.sentiment import SentimentAnalyzer
from nltk import word_tokenize
from nltk.sentiment.util import mark_negation
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
import csv
from cand_determiner import Determiner
from driver import CEU
import numpy as np
from sklearn.metrics import precision_recall_fscore_support as score

from sklearn.base import TransformerMixin

class SentimentAnalyzer:
    def __init__(self, tweet_data_loc=None):
        self.unigram_bigram_clf = Pipeline([
            ('vectorizer', CountVectorizer(analyzer="word",
                                           ngram_range=(1, 2), #now trigram
                                           tokenizer=word_tokenize,
                                           # tokenizer=lambda text: mark_negation(word_tokenize(text)),
                                           preprocessor=lambda text: text.replace("<br />", " "), )),
            ('classifier', SVC(kernel='linear', probability=True))
        ])
        self.train_X = []
        self.train_y = []
        self.test_X = []
        self.test_y = []
        self.train_basic_X = []
        self.train_basic_y = []
        self.test_basic_X = []
        self.test_basic_y = []

        self.cand_model = Determiner()
        self.ceu_model = CEU()

        self.model = None
        self.basic_model = None

        self.load_basic(tweet_data_loc)
        self.train_basic()
        self.load_train_data(tweet_data_loc)


    def evaluate_baseline(self, test_loc):
        for data_loc in test_loc:
            with open(data_loc, errors='ignore') as data_csv:
                csv_reader = csv.DictReader(data_csv, delimiter='\t')
                counter = 0
                for row in csv_reader:
                    if counter % 1000 == 0:
                        print("reading tweet " + str(counter))


                    counter += 1
                    content = row['TWEET']
                    # date = row['DATE']
                    label = row['LABEL']

                    if not content:
                        continue

                    self.test_basic_X.append(content)
                    self.test_basic_y.append(label)

                    if counter == 6000:
                        break
            break
        self.test_basic_X = np.array(self.test_basic_X)
        self.test_basic_y = np.array(self.test_basic_y)

        y_pred = self.basic_model.predict(self.test_basic_X)

        precision, recall, fscore, support = score(self.test_basic_y, y_pred)
        print('baseline:\n')
        print('precision: {}'.format(precision))
        print('recall: {}'.format(recall))
        print('fscore: {}'.format(fscore))
        print('support: {}'.format(support))
        #
        # print('f1, p, r for baseline')
        # print(f1_score(self.test_basic_y, y_pred))
        # print('\n')
        # print(precision_score(self.test_basic_y, y_pred))
        # print('\n')
        # print(recall_score(self.test_basic_y, y_pred))
        # print('\n')


    def load_test_data(self, test_loc):
        for data_loc in test_loc:
            with open(data_loc, errors='ignore') as data_csv:
                csv_reader = csv.DictReader(data_csv, delimiter='\t')
                counter = 0
                for row in csv_reader:
                    if counter % 1000 == 0:
                        print("reading test tweet " + str(counter))

                    counter += 1
                    content = row['TWEET']
                    # date = row['DATE']
                    label = row['LABEL']

                    if not content:
                        continue

                    polarities = self.basic_model.predict_proba([content])[0]
                    response, ne_list = self.cand_model.determine_candidacy(content, polarities)

                    new_content = None
                    # if ne_list and :
                    if response:
                        # go find some expanded data
                        new_content = self.ceu_model.find_text((row, ne_list))

                    if new_content:
                        self.test_X.append(new_content)
                    else:
                        self.test_X.append(content)
                    self.test_y.append(label)

                    if counter == 6000:
                        break
            break
        self.test_X = np.array(self.test_X)
        self.test_y = np.array(self.test_y)

    def run(self):
        y_pred = self.model.predict(self.test_X)

        precision, recall, fscore, support = score(self.test_y, y_pred)

        print('Ensemble:\n')
        print('precision: {}'.format(precision))
        print('recall: {}'.format(recall))
        print('fscore: {}'.format(fscore))
        print('support: {}'.format(support))

        # print(f1_score(self.test_y, y_pred))
        # print('\n')
        # print(precision_score(self.test_y, y_pred))
        # print('\n')
        # print(recall_score(self.test_y, y_pred))
        # print('\n')

    def load_train_data(self, train_loc):
        
        '''
        put training tweets through the new expanded model
        :return:
        '''

        for data_loc in train_loc:
            with open(data_loc, errors='ignore') as data_csv:
                csv_reader = csv.DictReader(data_csv, delimiter='\t')
                counter = 0
                for row in csv_reader:
                    if counter % 1000 == 0:
                        print("reading tweet " + str(counter))


                    counter += 1
                    content = row['TWEET']
                    # date = row['DATE']
                    label = row ['LABEL']



                    if not content:
                        continue

                    polarities = self.basic_model.predict_proba([content])[0]
                    response, ne_list = self.cand_model.determine_candidacy(content, polarities)
                    new_content = None
                    # if ne_list and :
                    if response:
                        #go find some expanded data
                        new_content = self.ceu_model.find_text((row, ne_list))

                    if new_content:
                        self.train_X.append(new_content)
                    else:
                        self.train_X.append(content)
                    self.train_y.append(label)

                    if counter == 6000:
                        break
            break
        self.train_X = np.array(self.train_X)
        self.train_y = np.array(self.train_y)

    def train_sent(self):
        self.model = self.unigram_bigram_clf.fit(self.train_X, self.train_y)
        print('ensemble_model trained')

    def load_basic(self, train_loc):
        for data_loc in train_loc:
            with open(data_loc, errors='ignore') as data_csv:
                csv_reader = csv.DictReader(data_csv, delimiter='\t')
                counter = 0
                for row in csv_reader:
                    if counter % 1000 == 0:
                        print("reading tweet " + str(counter))


                    counter += 1
                    content = row['TWEET']
                    # date = row['DATE']
                    label = row ['LABEL']

                    if not content:
                        continue

                    self.train_basic_X.append(content)
                    self.train_basic_y.append(label)

                    if counter == 6000:
                         break
            break
        self.train_basic_X = np.array(self.train_basic_X)
        self.train_basic_y = np.array(self.train_basic_y)

    def train_basic(self):
        self.basic_model = self.unigram_bigram_clf.fit(self.train_basic_X, self.train_basic_y)
        print('basic model trained')
    
    def classify_instance(self, text):
        return self.model.classify(text)