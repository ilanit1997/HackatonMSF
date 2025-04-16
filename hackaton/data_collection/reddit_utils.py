import os
import praw
import pandas as pd
import re
import datetime
from tqdm import tqdm


def extract_between_brackets(text):
    pattern = r'\[(.*?)\]'
    matches = re.findall(pattern, text)
    return matches


def remove_text_between_brackets(text):
    pattern = r'\[.*?\]'
    result = re.sub(pattern, '', text)
    return result


def num_words(text):
    try:
        return len(text.split())
    except:
        return 0


def convert_utc_to_datetime(utc_time):
    return datetime.datetime.utcfromtimestamp(utc_time).strftime('%d/%m/%y %H:%M:%S')


def remove_text_after_x(text, x):
    pattern = re.escape(x) + r'.*'
    result = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return result


def extract_data_from_comment(comment, prefix=None):
    data = dict(comment_id=comment.id, comment_body=remove_text_after_x(comment.body, 'edit:'),
                comment_author=comment.author.name if comment.author is not None else None,
                comment_date_time=convert_utc_to_datetime(comment.created), comment_score=comment.score)
    if prefix is not None:
        data = {f"{prefix}_{k}": v for k, v in data.items()}
    return data


def extract_data_from_post(post):
    post_data = dict(post_id=post.id, title=remove_text_between_brackets(post.title),
                     post_author=post.author.name if post.author is not None else None,
                     body=remove_text_after_x(post.selftext, 'edit:'), date_time=convert_utc_to_datetime(post.created),
                     url=post.url, score=post.score, num_comments=post.num_comments)
    post_data['flairs'] = str(extract_between_brackets(post.title))
    comments = [(comment, comment.score, num_words(comment.body)) for comment in post.comments]
    comments = [x for x in comments if x[2] > 30]
    if len(comments) == 0:
        return post_data
    highest_comment = sorted(comments, key=lambda c: c[1], reverse=True)[0][0]
    if len(comments) == 1:
        post_data.update(extract_data_from_comment(highest_comment, 'highest'))
        post_data.update(extract_data_from_comment(highest_comment, 'longest'))
        return post_data
    longest_comment = sorted(comments, key=lambda c: c[2], reverse=True)[0][0]
    post_data.update(extract_data_from_comment(highest_comment, 'highest'))
    post_data.update(extract_data_from_comment(longest_comment, 'longest'))
    return post_data