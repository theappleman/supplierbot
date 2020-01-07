from botfriend.bot import TextGeneratorBot
import requests


class Supplier(TextGeneratorBot):

    api_host = "https://yande.re"

    def update_state(self):
        posts = requests.get("{}/post.json".format(self.api_host), params={
            "tags": "thighhighs",
        })

        return posts.json()

    def generate_text(self):
        posts = self.model.json_state

        recent_posts = [
            recent.content
            for recent in self.model.recent_posts(365)
        ]

        chosen = None
        for post in posts:
            if chosen:
                break
            if post['rating'] != 's':
                continue

            tags = [f"#{tag}" for tag in post['tags'].split(" ")]
            content = "{} {}/post/show/{}".format(
                            " ".join(tags),
                            self.api_host,
                            post['id']
                        )

            if content in recent_posts:
                continue

            sample = requests.get(post['sample_url'], stream=True)

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
