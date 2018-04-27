import os
from pathlib import Path
import subprocess

# for file in os.listdir('4-English_train_dev/Subtask_A'):
#     new_path = os.path.join('4-English_train_dev/Subtask_A', file)
#     if new_path[-4:] == '.txt':
#         print(new_path)
#         Path('python download_tweets_user_api.py --dist' + new_path + ' --output' + 'dev.txt --user')
#         break

root_path = Path('4-English_train_dev/Subtask_A')
for child in root_path.iterdir():
    if child.suffix == '.txt':
        print(child)
        subprocess.run(['python', 'download_tweets_user_api.py', '--dist', str(child), '--output', 'dev.txt', '--user'])
        break
