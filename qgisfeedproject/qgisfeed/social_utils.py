from django.conf import settings
from mastodon import Mastodon

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