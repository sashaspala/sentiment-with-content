import os
from pathlib import Path
from ast import literal_eval

root_path = Path('twitter_download-master/output_nonformatted/test')


to_nums = {'neutral' : '0', 'positive' : '1', 'negative' : '-1'}

def read_batch(batch, year, year_dicts, outfile):
    if year not in year_dicts:
        with open('twitter_download-master/4-English_train_dev/Subtask_A/' + year) as ref_file:
            lines = ref_file.readlines()
        temp_dict = {}
        for line in lines:
            args = line.split('\t')
            temp_dict[args[0]] = to_nums[args[1].strip()]
        year_dicts[year] = temp_dict

    for entry in batch:
        tweet = entry['text'].replace('\n', '')
        user = entry['user']['screen_name']
        id = str(entry['id'])
        label = year_dicts[year][id]
        date = entry['created_at']

        outfile.write(id + '\t' + label + '\t' + tweet + '\t' + date + '\t' + user + '\n')

    return year_dicts

year_dicts = {}

with open('twitter_2013-2016_test.csv', 'w') as out_file:
    out_file.write('ID\tLABEL\tTWEET\tDATE\tSOURCE_USER\n')
    for child in root_path.iterdir():
        if child.suffix == '.txt' and child.stem[-4:] != 'full':
            year = child.stem[:-7]
            with child.open() as in_file:
                lines = in_file.readlines()
                for line in lines:
                    batch = literal_eval(line)
                    year_dicts = read_batch(batch, year, year_dicts, out_file)






