from nltk.classify import NaiveBayesClassifier
from trainer import SentimentAnalyzer
from cand_determiner import Determiner
from db_driver import KnowledgeSource
import re
import csv

class Driver:
    def __init__(self):
        self.train_model()

        self.cand_model = Determiner()
        self.expander = CEU()

    def train_model(self):
        # sent_model = SentimentAnalyzer(['training.1600000.processed.noemoticon.csv'])
        sent_model = SentimentAnalyzer(['twitter_2013-2016_train.csv'])
        self.sent_driver = sent_model
        sent_model.train_sent()



    def evaluate(self, baseline=False):
        self.sent_driver.load_test_data(['twitter_2013-2016_dev.csv'])

        if baseline:
            print(self.sent_driver.evaluate_baseline(['twitter_2013-2016_dev.csv']))
        print(self.sent_driver.run())
    # def classify_tweet(self, tweet_data, source):
    #     polarities = self.basic_model.predict_proba(tweet_data['TWEET'])
    #     response, ne_list = self.cand_model.determine_candidacy(tweet_data['TWEET'], polarities)
    #
    #     if response:
    #         new_text = self.expander.find_text((tweet_data, ne_list))
    #         if new_text:
    #             self.sentiment_model.classify(new_text)
    #     return #sentiment somehow

class CEU:
    def __init__(self):
        self.knowledge_model = KnowledgeSource()

        self.months = {'Jan': '01', 'Feb': '02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}
    
    def get_metadata(self, data):
        '''
        return a dictionary with fields {DATE, AT_USER, SOURCE_USER, REPLY, HASHTAG}
        :param tweet: 
        :return: 
        '''
        metadata = {}
        if "DATE" in data and data['DATE']:
            #year month day
            split_date = data['DATE'].split()
            # if split_date[5] == '2011':
            #     print('in date range now')
            metadata["DATE"] = split_date[5] + self.months[split_date[1]] + split_date[2]

        text = data['TWEET']
        if '@' in text:
            metadata['AT_USER'] = [after_at.split()[0] for after_at in text.split('@') if len(after_at.split()) > 0]

        if '#' in text:
            metadata['HASHTAG'] = [after_hash.split()[0] for after_hash in text.split('#') if len(after_hash.split()) > 0]

        if 'USER' in data and data['USER']:
            metadata['SOURCE_USER'] = data['USER']

        return metadata
    
    def find_text(self, tweet_data_tuple):
        meta_data = self.get_metadata(tweet_data_tuple[0])
        
        score, text_to_append = self.knowledge_model.find_context(meta_data, tweet_data_tuple[1])
        if score:
            new_text = tweet_data_tuple[0]['TWEET'] + ' ' + text_to_append
            return new_text
        return None



if __name__ == '__main__':
    #go through tweets and feed to system
    system_driver = Driver()
    system_driver.evaluate(baseline=True)



    
    
   
        
