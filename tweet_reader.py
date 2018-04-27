import csv

class Reader:
    def __init__(self):
        pass

    def open_file(self, filepath):
        with open(filepath, errors='ignore') as tweet_file:
            csv_reader = csv.reader(tweet_file)

            for row in csv_reader:
                # print(row)
                if row[4] == 'katyperry':
                    print(row)


if __name__ == '__main__':
    reader = Reader()
    reader.open_file('training.1600000.processed.noemoticon.csv')

  