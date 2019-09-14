import configparser
import datetime
import logging

import praw
import requests


def get_twitch_data(session, config):
    """
    Fetches basic data about a Twitch stream.
    :param session: An instance of `request.Session()`
    :param config: An instance of `configparser.ConfigParser()` with Twitch
    auth credentials and a streamer name
    :return: A dictionary with stream status, url. If status is Online the dict
    also has game name, box art, and viewer count.
    """

    headers = {'Client-ID': config['TwitchAuth']['ClientID']}
    params = {'user_login': config['TwitchStream']['Name']}
    response = session.get('https://api.twitch.tv/helix/streams',
                           params=params, headers=headers)
    if response.status_code == 200:
        logging.info('Twitch authentication successful.')
    else:
        logging.error('Twitch authentication failed. %s', response.json())
    twitch_url = 'https://twitch.tv/' + config['TwitchStream']['Name']

    try:
        game_id = response.json()['data'][0]['game_id']
        game_params = {'id': game_id}
        game_data = session.get('https://api.twitch.tv/helix/games',
                                params=game_params, headers=headers)

        game_name = game_data.json()['data'][0]['name']
        box_art_url_template = game_data.json()['data'][0]['box_art_url']
        box_art_url = box_art_url_template.format(width=100, height=100)
        viewer_count = response.json()['data'][0]['viewer_count']

        twitch_data = {'status': 'Online',
                       'url': twitch_url,
                       'game_name': game_name,
                       'game_box_art': box_art_url,
                       'viewer_count': viewer_count}
        logging.info('Stream status: %s. Game: %s, Viewer count: %s',
                     twitch_data['status'], twitch_data['game_name'],
                     twitch_data['viewer_count'])

    except (IndexError, KeyError):
        twitch_data = {'status': 'Offline',
                       'url': twitch_url}
        logging.info('Stream status: %s.', twitch_data['status'])

    return twitch_data


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
    now = datetime.datetime.utcnow()
    created = datetime.datetime.fromtimestamp(post.created_utc)
    delta = created - now
    recent_seconds = hours * 60 * 60
    if delta.seconds < recent_seconds:
        return True
    else:
        return False


def submit_thread(config, reddit, title, content):
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
    else:
        logging.info('Found a recent bot thread. Skipped creating a new one.')



if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    with open("config.ini") as f:
        config = configparser.ConfigParser()
        config.read_file(f)

    reddit = praw.Reddit(client_id=config['RedditAuth']['ClientID'],
                         client_secret=config['RedditAuth']['ClientSecret'],
                         refresh_token=config['RedditAuth']['RefreshToken'],
                         user_agent=config['RedditAuth']['UserAgent'])

    session = requests.Session()
    twitch_data = get_twitch_data(config=config, session=session)

    if config['Subreddit'].getboolean('UpdateWidget') is True:
        widget_template = create_widget(twitch_data)
        update_widget(config=config, reddit=reddit, widget_source=widget_template)

    if config['Subreddit'].getboolean('PostThread') is True:
        if twitch_data['status'] is 'Online':
            content = create_thread_content(twitch_data)
            title = create_thread_title(twitch_data)
            submit_thread(config=config, reddit=reddit, title=title, content=content)
