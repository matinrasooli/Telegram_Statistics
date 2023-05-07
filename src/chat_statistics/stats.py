
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Union

import arabic_reshaper
from bidi.algorithm import get_display
from hazm import Normalizer, sent_tokenize, word_tokenize
from wordcloud import WordCloud

from src.data import DATA_DIR


class ChatStatistics:
    def __init__(self, chat_json: Union[str, Path]):
        with open(chat_json) as f:
            self.chat_data = json.load(f)

        stop_words = open(DATA_DIR / 'stopwords.txt').readlines()
        stop_words = set(map(str.strip, stop_words))   

    
    def get_top_users(self, top_n: int = 10) -> dict:

        # check messages for questions
        is_question = defaultdict(bool)
        for msg in self.chat_data['messages']:
            if not isinstance(msg['text'], str):
                msg['text'] = self.rebuild_msg(msg['text'])
            sentences = sent_tokenize(msg['text'])
            for sentence in sentences:
                if "?" in msg['text'] or "؟" in msg['text']:
                    continue
                is_question[msg['id']] = True
                break
        
        # get top users based on replying to questions from others
        users = []
        for msg in self.chat_data['messages']:
            if not msg.get('reply_to_message_id'):
                continue
            # users[msg['from_id']].append(msg['reply_to_message_id'])
            if is_question[msg['reply_to_message_id']] is False:
                continue
            users.append(msg['from'])
        return dict(Counter(users).most_common(top_n))
        

    def generate_word_cloud(self, output_dir):
        text_content = ''

        for msg in self.chat_data['messages']:
            if type(msg['text']) is str:
                text_content += f" {msg['text']}"

        text_content = arabic_reshaper.reshape(text_content)
        text_content = get_display(text_content)

        wordcloud = WordCloud(font_path=str(DATA_DIR / 'BHoma.ttf'), background_color='white',width=900,height=900).generate(text_content)

        wordcloud.to_file(str(Path(output_dir) / 'wordcloud.png'))
        
    @staticmethod
    def rebuild_msg(sub_messages):
        msg_text=''
        for sub_msg in sub_messages:
            if isinstance(sub_msg, str):
                msg_text += sub_msg
            elif 'text' in sub_msg:
                msg_text += sub_msg['text']
        return msg_text

    def msg_has_question(self, msg):

    
        if not isinstance(msg['text'], str):
            msg['text'] = self.rebuild_msg(msg['text'])
        sentences = sent_tokenize(msg['text'])
        for sentence in sentences:
            if "?" in msg['text'] or "؟" in msg['text']:
                continue
            return True


if __name__ == "__main__":
    chat_stats = ChatStatistics(chat_json = DATA_DIR / 'online.json')
    top_users = chat_stats.get_top_users(top_n=10)
    print(top_users)
    chat_stats.generate_word_cloud(output_dir = DATA_DIR)
    