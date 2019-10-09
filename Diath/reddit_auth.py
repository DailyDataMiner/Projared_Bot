import configparser
import praw

def auth():
    with open("../config.ini") as f:
        config = configparser.ConfigParser()
        config.read_file(f)

    if not config['RedditAuth']['RefreshToken']:
        reddit = praw.Reddit(client_id=config['RedditAuth']['ClientID'],
                             client_secret=config['RedditAuth']['ClientSecret'],
                             redirect_uri=config['RedditAuth']['RedirectURI'],
                             user_agent=config['RedditAuth']['UserAgent'])

        if not config['RedditAuth']['Code']:
            scopes = config['RedditAuth']['Scopes'].split(',')
            print(reddit.auth.url(scopes, 'basic', 'permanent'))
        else:
            refresh_token = reddit.auth.authorize(config['RedditAuth']['Code'])
            print('RefreshToken:', refresh_token)

    else:
        reddit = praw.Reddit(client_id=config['RedditAuth']['ClientID'],
                             client_secret=config['RedditAuth']['ClientSecret'],
                             refresh_token=config['RedditAuth']['RefreshToken'],
                             user_agent=config['RedditAuth']['UserAgent'])
        print(f'Successfully authenticated user {reddit.user.me()}. Scopes: {reddit.auth.scopes()}')
        return reddit

if __name__ == '__main__':
    auth()
