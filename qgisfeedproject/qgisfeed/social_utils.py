from django.conf import settings
from mastodon import Mastodon
from atproto import Client, client_utils

class MastodonManager:
  def __init__(self):
    self.mastodon = Mastodon(
      access_token=settings.MASTODON_ACCESS_TOKEN,
      api_base_url=settings.MASTODON_API_BASE_URL,
    )

  def create_post(self, status, image_path=None):
    media_ids = None
    if image_path:
      media = self.mastodon.media_post(image_path)
      media_ids = [media['id']]
    return self.mastodon.status_post(status, media_ids=media_ids)

class BlueskyManager:
  def __init__(self):
    self.client = Client()
    self.client.login(
      settings.BLUESKY_HANDLE,
      settings.BLUESKY_PASSWORD,
    )

  def build_text(self, title, content):
    text_builder = client_utils.TextBuilder()
    text_builder.text(title)
    text_builder.text('\n\n')
    text_builder.text(content)
    return text_builder
  
  def create_post(self, text_builder, image:bytes = None):
    if image:
      post = self.client.send_image(
        text=text_builder,
        image=image,
        image_alt=''
      )
    else:
      post = self.client.send_post(text_builder)
    return post
