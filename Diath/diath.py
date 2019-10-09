import configparser
import datetime
import time
import calendar
import logging
import json

import praw
import prawcore
import requests

def create_widget(twitch_data):
    """
    Generates markdown source for a custom Reddit widget.
    :param twitch_data: A dictionary with Twitch stream info.
    :return: A string of formatted markdown.
    """

    if twitch_data['status'] == 'Online':
        widget_source = f'''
        ##Twitch.tv

        * [Online]({twitch_data['url']})
        * Streaming: {twitch_data['game_name']}
        * Viewers: {twitch_data['viewer_count']}
        '''

    elif twitch_data['status'] == 'Hosting':
        widget_source = f'''
        ##Twitch.tv

        * [Hosting]({twitch_data['url']})
        * Host: {twitch_data['host']}
        * Link: {twitch_data['url']}
        '''
    
    else:
        widget_source = f'''
        ##Twitch.tv

        * [Offline]({twitch_data['url']})
        '''

    return widget_source

def update_widget(config, reddit, widget_source):
    """
    Updates a custom reddit widget.
    :param config: An instance of `configparser.ConfigParser()` with subreddit
    and widget names.
    :param reddit: An instance of `praw.Reddit()` with proper auth.
    :param widget_source: A string of formatted markdown.
    """

    widgets = reddit.subreddit(config['Subreddit']['Name']).widgets
    twitch_widget_name = config['Subreddit']['WidgetTitle']

    try:
        twitch_widget = [widget for widget in widgets.sidebar
                         if widget.shortName == twitch_widget_name][0]
        twitch_widget.mod.update(text=widget_source)
        logging.info('Widget update successful.')

    except IndexError:
        logging.error('No widget named %s. Check the name '
                      'in the config or create a new widget on the subreddit.',
                      twitch_widget_name, exc_info=True)
        return 500
    return 200

def create_thread_title(twitch_data):
    """
    Generates a title for a Reddit thread.
    :param twitch_data: A dictionary with Twitch stream info.
    :return: A string with a date and a streamed game.
    Example: Sunday, Jan 12 stream: Tetris - discussion
    """

    today = datetime.date.today()
    date_formatted = today.strftime('%A, %b %d')
    title = f'{date_formatted} stream: {twitch_data["game_name"]} - discussion'
    return title

def create_thread_content(twitch_data):
    """
    Generates the body of a Reddit thread.
    :param twitch_data: A dictionary with Twitch stream info.
    :return: A string of formatted markdown.
    """

    # TODO: create a template for the thread content. Something short with
    #       basic info that encourages discussion.
    content = f'''
    Content goes here

    More content

    Maybe some [link]({twitch_data['url']})
    '''

    return content

def is_post_recent(post, hours=12):
    """
    Checks if a reddit post was made recently (less than 12 hours by default).
    :param post: Reddit post as an instance of praw.models.Submission()
    :param hours: Integer; how many hours are defined as recent for our purpose.
    :return: Boolean.
    """

    now = int(time.time())
    created = post.created_utc
    print('Created: ' + str(created) + ' now: ' + str(now))
    delta = now - created
    print('Delta: ' + str(delta))
    recent_seconds = hours * 60 * 60
    if int(delta) < recent_seconds:
        return True
    else:
        return False

def submit_thread(config, reddit, title, content, thread_path):
    """
    Checks the last 50 posts on a given subreddit. If there are no recent posts
    made by the bot, creates (and optionally stickies) a new one.
    :param config: An instance of `configparser.ConfigParser()` with subreddit
    and bot posting options.
    :param reddit: An instance of `praw.Reddit()` with proper auth.
    :param title: String; thread title.
    :param content: String; a markdown-formatted body of the thread.
    """

    subreddit = reddit.subreddit(config['Subreddit']['Name'])
    new_posts = subreddit.new(limit=50)
    bot_posts = (post for post in new_posts if post.author == reddit.user.me())
    recent_posts = (post for post in bot_posts if is_post_recent(post))

    if not any(recent_posts):
        thread = subreddit.submit(title, selftext=content)
        logging.info('Created a new Reddit thread: %s', thread.url)
        if config['Subreddit'].getboolean('StickyThread') is True:
            thread.mod.sticky()
        update_thread(thread_path=thread_path, thread=thread)
    else:
        logging.info('Found a recent bot thread. Skipped creating a new one.')

def update_thread(thread_path, thread):
    data = {}
    data['thread'] = []
    data['thread'].append({
        'id': str(thread.id),
        'timestamp': str(thread.created_utc)
    })
    text_data = json.dumps(data)
    thread_path.write_text(text_data)
    return

def submit(twitch_data, thread_path):

    with open("config.ini") as f:
        config = configparser.ConfigParser()
        config.read_file(f)

    try:
        reddit = praw.Reddit(client_id=config['RedditAuth']['ClientID'],
            client_secret=config['RedditAuth']['ClientSecret'],
            refresh_token=config['RedditAuth']['RefreshToken'],
            user_agent=config['RedditAuth']['UserAgent'])
    except:
        logging.error('Failed to authenticate with Reddit.')

    if config['Subreddit'].getboolean('UpdateWidget') is True:
        widget_template = create_widget(twitch_data)
        update_widget(config=config, reddit=reddit, widget_source=widget_template)

    if config['Subreddit'].getboolean('PostThread') is True:
        if twitch_data['status'] is 'Online':
            content = create_thread_content(twitch_data)
            title = create_thread_title(twitch_data)
            submit_thread(config=config, reddit=reddit, title=title, content=content, thread_path=thread_path)
        elif twitch_data['status'] is 'Offline':
            ## Does something to check the current status of the tread and whether to unsticky it or not
            pass
    
    return 200

def reddit_call(twitch_data):
    logging.info('Entering check() of diath.py')
    with open("config.ini") as f:
        config = configparser.ConfigParser()
        config.read_file(f)

    # Authenticates and returns an instance of reddit
    reddit = praw.Reddit(client_id=config['RedditAuth']['ClientID'],
        client_secret=config['RedditAuth']['ClientSecret'],
        refresh_token=config['RedditAuth']['RefreshToken'],
        user_agent=config['RedditAuth']['UserAgent'])

    widget = create_widget(twitch_data)

    status = update_widget(config, reddit, widget)

    ## This is here in case we gotta start on thread functionality again
    # for submission in reddit.redditor(str(reddit.user.me())).submissions.new(limit=1):
    #     if is_post_recent(submission) == True:
    #         logging.info('Thread is too new.')
    #         return 200
    #     else:
    #         try:
    #             for sticky in reddit.subreddit(config['Subreddit']['Name']).sticky():
    #                 logging.info('Sticky thread found')
    #                 sticky.num_comments
    #                 if subs.num_comments >= config['Subreddit']['CommentLimit']:
    #                     pass
    #                     # Unsticky the thread
    #                 else:
    #                     pass
    #                     # Unsticky, Delete the thread
    #                 pass
    #         except:
    #             logging.info("No sticky thread found.")

    logging.info('Exiting check() of diath.py')
    return status