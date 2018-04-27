from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
class Determiner:
    '''
    Does named entity recognition and extraction
    '''
    def __init__(self):
        self.polarity_threshold = .9

    #based off of https://stackoverflow.com/questions/31836058/nltk-named-entity-recognition-to-a-python-list
    def get_named_entities(self, tweet):
        tree_chunk = ne_chunk(pos_tag(word_tokenize(tweet)))
        all_ne = []
        curr_chunk = []

        for item in tree_chunk:
            #if its another tree, keep recursing
            if type(item) == Tree:
                curr_chunk.append(" ".join([token for token, pos in item.leaves()]))
            elif curr_chunk:
                ne = ' '.join(curr_chunk)
                if ne not in curr_chunk:
                    # all_ne.append(ne)
                    all_ne.extend(curr_chunk)
                    curr_chunk = []

            else:
                continue

        return all_ne

    def determine_candidacy(self, tweet, polarities):
        if all(value <= self.polarity_threshold for value in polarities):
            ne = self.get_named_entities(tweet)
            if len(ne) > 0:
                return True, ne
        return False, None
            
