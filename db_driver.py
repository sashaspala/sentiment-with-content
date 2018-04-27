import os
import csv
import pandas as pd
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import datetime
from ast import literal_eval

from nltk.sem import relextract

class KnowledgeSource:
    def __init__(self, models=['reuters']):
        self.models = models
        self.max_date_range = 20
        self.k = 10

        if 'news-aggregator' in self.models:
            self.load_agg()

        self.reuters_years = {}
        self.load_reuters()

    def load_reuters(self):
        for csv_file in os.listdir('knowledge_base/reuters-news-wire-archive'):
            new_path = os.path.join('knowledge_base/reuters-news-wire-archive', csv_file)
            if new_path[-3:] == 'csv':
                temp_dict = {}
                with open(new_path) as input_file:
                    for line in input_file.readlines():
                        if line != '\n':
                            args = line.split('\t')
                            if args[0][:8] not in temp_dict:
                                temp_dict[args[0][:8]] = [(literal_eval(args[1]), args[2])]
                            else:
                                temp_dict[args[0][:8]].append((literal_eval(args[1]), args[2]))

                self.reuters_years[new_path[-18:-14]] = temp_dict

    def load_agg(self):
        with open('knowledge_base/news-aggregator/uci-news-aggregator.csv') as agg_csv:
            self.agg_reader = csv.DictReader(agg_csv)

    def comb_agg(self, meta_data, ne_list):
        possible_dates = []
        if 'DATE' in meta_data:
            possible_dates = self.create_date_range(meta_data['DATE'][:8])

        possible_hits = []

        for row in self.agg_reader:
            date= datetime.datetime.fromtimestamp(int(row['TIMESTAMP'])).strftime('%Y%m%d %H:%M:%S').split()[0]
            if possible_dates and date >= possible_dates[0] and date <= possible_dates[len(possible_dates)-1]:
                possible_hits.extend(self.relation_extraction(ne_list, row['TITLE']))
            elif not possible_dates:
                possible_hits.extend(self.relation_extraction(ne_list, row['TITLE']))

        return possible_hits


    def find_context(self, meta_data, ne_list):
        results = self.search_reuters(meta_data, ne_list)

        if 'new-aggregator' in self.models:
            results.extend(self.comb_agg(meta_data, ne_list))

        if 'all-the-news' in self.models:
            pass

        # results.sort(key=lambda x:x[0])

        if results:
            return results[0]
        else:
            return None, None

    def search_reuters(self, meta_data, ne_list):
        start_year = None
        end_year = None
        possible_dates = []
        possible_hits = [(0, None) for index in range(self.k)]

        if 'DATE' in meta_data:
            possible_dates = self.create_date_range(meta_data['DATE'][:8])
            start_year = possible_dates[0][:4]
            end_year = possible_dates[len(possible_dates)-1][:4]

            for year in self.reuters_years:
                if year == start_year or year == end_year:
                     for date in possible_dates:
                        if date in self.reuters_years[year]:
                            temp_date_score = self.max_date_range - abs(int((datetime.date(int(meta_data['DATE'][:4]), int(meta_data['DATE'][4:6]), int(meta_data['DATE'][6:]))
                                                                            - datetime.date(int(date[:4]), int(date[4:6]), int(date[6:]))).days))
                            #found a match:
                            headlines = self.reuters_years[year][date]
                            possible_hits = self.comb_reuters_file(ne_list, headlines, temp_date_score, possible_hits)

                if year == end_year:
                        break
        if possible_hits[0][0] > 2:
            print(possible_hits)
            return possible_hits
        return None

    def comb_reuters_file(self, ne_list, headlines, date_score, top_k_scores):
        # top_k_scores = [(0, None) for index in range(self.k)]
        for news_ne, text in headlines:
            int_score = self.relation_extraction(ne_list, news_ne)
            if int_score > 0:
                multiplier = 1
            else:
                multiplier = 0
            score = (int_score + date_score) * multiplier
            if score > top_k_scores[len(top_k_scores) - 1][0]:
                top_k_scores = top_k_scores[:-1]
                top_k_scores.append((score, text))
                top_k_scores.sort(key=lambda x: x[0], reverse=True)

                if len(top_k_scores) > 10:
                    top_k_scores = top_k_scores[:-1]
            elif score == top_k_scores[len(top_k_scores) - 1][0] and score != 0:
                top_k_scores.append((score, text))
                top_k_scores.sort(key=lambda x: x[0], reverse=True)
        return top_k_scores


    def relation_extraction(self, ne_list, news_ne):
        '''
        provides a response tuple of (score, text) based on relation extraction between ne_list and the news_text
        :param ne_list:
        :param news_text:
        :return:
        '''

        ##Temp placeholder for better model

        score = 0
        for ne in news_ne:
            if ne in ne_list:
                score += 1
        return score

    def get_named_entities(self, tweet):
        tree_chunk = ne_chunk(pos_tag(word_tokenize(tweet)))
        all_ne = []
        curr_chunk = []

        for item in tree_chunk:
            # if its another tree, keep recursing
            if type(item) == Tree:
                curr_chunk.append(" ".join([token for token, pos in item.leaves()]))
            elif curr_chunk:
                ne = ' '.join(curr_chunk)
                if ne not in curr_chunk:
                    all_ne.extend(curr_chunk)
                    # all_ne.append(ne)
                    curr_chunk = []

            else:
                continue

        return all_ne

    def create_date_range(self, date):
        #give dates within
        middle = date[:4] + '-' + date[4:6] + '-' + date[6:]
        left_range = list(pd.date_range(end=middle, periods=self.max_date_range))
        right_range = list(pd.date_range(middle, periods=self.max_date_range))

        full_range = left_range + right_range
        return [''.join(str(date_in_range).split()[0].split('-')) for date_in_range in full_range]



