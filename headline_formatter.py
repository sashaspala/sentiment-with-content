
from pathlib import Path
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree


def get_named_entities(tweet):
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
                all_ne.append(ne)
                all_ne.extend(curr_chunk)
                curr_chunk = []

        else:
            continue

    return all_ne

root_path = Path('knowledge_base/reuters-news-wire-archive')
for child in root_path.iterdir():
    if child.suffix == '.csv':
        with child.open() as infile:
            lines = infile.readlines()

        with open(str(child.stem) + '_formatted.csv', 'w') as outfile:
            c = 0
            for line in lines[1:]:
                if c % 4000 == 0:
                    print(c)

                c += 1
                if line == '\n':
                    continue

                args = line.split(',')
                timestamp = args[0]
                counter = timestamp[-4:]

                if int(counter) > 150:
                    continue

                ne = get_named_entities(args[1])
                if ne:
                    outfile.write(args[0] + '\t' + str(ne) + '\t' + args[1] + '\n')

