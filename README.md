# sentiment-with-content
2018 Spring IE final project

This system works through the SemEval Task 4 dataset for Twitter message polarity to expand the content of tweets based on the content of the original tweet and headlines and news articles from similar dates and similar content.

The system first classifies an incoming tweet based on a basic sentiment analysis model, trained on regular 140 and 280 character tweets. Given the polarity probabilities and the results of NER run on the tweet, the candidate classifier determines whether the tweet is a good candidate for expanded content. If the model is unsure of the label, i.e. all probabilities fall below a threshold score, it should benefit from more content.

After a tweet is determined to be a candidate, it is sent to the Content Expansion Unit to gather metadata (hashtags, @, and most importantly, dates). The date of the tweet is used to narrow the search space when looking for related content.

Using the NER on the headlines and news articles to measure overlap between the tweet and the reference content, as well as semantic similarity between the two and the temporal distance of the reference content from the date of the original tweet, the content is scored and the k-best scoring documents/headlines kept. 

The best scoring (read: best match) document is appended to the original tweet and sent through a semantic analysis model that is specifically trained on these expanded tweet + reference document Frankenstein documents. 

I believe most of the problem with this model stems from the vast search space of the documents. I believe that this model would benefit from full articles, but the current architecture isn't set up for a parallelized task. Expanding this to full documents, as well as more evaluation techniques for the semantic similarity between the tweet and a headline would be very helpful as there are currently many false matches based on the high impact of named entity, which are common in headlines, but lack the relation information for why those NE might be important for this specific tweet or headline. This is begging to be distributed into a MapReduce system, but I don't currently have those resources or access to a nice cluster. :)

Find my presentation here: https://docs.google.com/presentation/d/14DzEpaZDd88BAeNAevnL93XkvSibR2Z4_8r0eQc--_E/edit?usp=sharing
![System Architecture](sentiment_full_architechture - Page 1.png?raw=true "System Architecture")
