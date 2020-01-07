from botfriend.bot import TextGeneratorBot
from botfriend.model import _now
import requests
from textblob import TextBlob


class ApiHost(object):
    def url(self, request_uri):
        return "{}://{}{}".format(self.scheme, self.domain, request_uri)

    def __init__(self, domain,
                 scheme=None,
                 post_path=None,
                 api_path=None,
                 tags=None,
                 preview=None,
                 ):
        self.scheme = scheme or "https"
        self.domain = domain
        self.post_path = post_path or "/post/show/"
        self.api_path = api_path or "/post.json"
        self.tags = tags or "tags"
        self.preview = preview or "sample_url"


class Supplier(TextGeneratorBot):

    @property
    def api_host(self):
        case = [
            ApiHost("yande.re"),
            ApiHost("konachan.net"),
            ApiHost("hypnohub.net"),
            ApiHost("danbooru.donmai.us",
                    api_path="/posts.json",
                    tags="tag_string",
                    preview="file_url"),
        ]

        return case[_now().toordinal() % len(case)]

    def update_state(self):
        posts = requests.get(
                self.api_host.url(self.api_host.api_path),
                params={
                    "tags": "thighhighs",
                })

        return {
            "host": self.api_host.domain,
            "post": "{} " + self.api_host.url(self.api_host.post_path) + "{}",
            "tags": self.api_host.tags,
            "sample": self.api_host.preview,
            "posts": posts.json(),
        }

    def generate_text(self):
        state = self.model.json_state
        posts = state['posts']

        recent_posts = [
            TextBlob(recent.content)
            for recent in self.model.recent_posts(365)
        ]
        # alnum + underscore
        tr = {x: None for x in
                list(range(ord('A'), ord('Z'))) +
                list(range(ord('a'), ord('z'))) +
                list(range(ord('0'), ord('9'))) +
                [ord('_')]}

        chosen = None
        for post in posts:
            if chosen:
                break
            if post['rating'] != 's':
                continue

            tags = [f"#{tag}" for tag in post[state['tags']].split(" ")
                    if tag.translate(tr) == '']
            content = state['post'].format(
                            " ".join(tags),
                            post['id']
                        )

            if content in recent_posts:
                continue

            sample = requests.get(post[state['sample']], stream=True)

            with open("{}.jpg".format(post['md5']), "wb") as f:
                for chunk in sample:
                    f.write(chunk)

            attachment = {
                "path": "../{}.jpg".format(post['md5']),
                "type": sample.headers['Content-Type'],
            }

            selected = {
                "key": post['md5'],
                "content": content,
                "attachments": [attachment],
            }

            if selected:
                chosen = selected

        return chosen


Bot = Supplier
