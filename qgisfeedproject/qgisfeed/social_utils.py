from django.conf import settings
from mastodon import Mastodon
from atproto import Client, client_utils
import requests

class MastodonManager:
  """
  MastodonManager provides an interface to interact with the Mastodon social platform.
  This class handles authentication, text building,
  and posting (with or without images) to Mastodon using the provided client utilities.
  Methods
  -------
  __init__():
    Initializes the MastodonManager instance and logs in using credentials from settings.
  build_text(title, content):
    Constructs a text builder object with the given title and content, separated by two newlines.
  create_post(text_builder, image: bytes = None):
    Creates a post on Mastodon using the provided text builder. If an image is provided, posts with the image; otherwise, posts text only.
  """
  def __init__(self):
    self.mastodon = Mastodon(
      access_token=settings.MASTODON_ACCESS_TOKEN,
      api_base_url=settings.MASTODON_API_BASE_URL,
    )

  def create_post(self, status: str, image_path: str = None):
    """
    Creates a post on Mastodon using the provided status and optional image path.
    If an image path is provided, posts with the image; otherwise, posts text only.
    Parameters
    ----------
    status : str
      The text content of the post.
    image_path : str, optional
      The path to the image to be included in the post. If not provided, only text will be posted.
    Returns
    -------
    mastodon.models.Status
      The created status object.
    """
    media_ids = None
    if image_path:
      media = self.mastodon.media_post(image_path)
      media_ids = [media['id']]
    return self.mastodon.status_post(status, media_ids=media_ids)

class BlueskyManager:
  """
  BlueskyManager provides an interface to interact with the Bluesky social platform.
  This class handles authentication, text building, 
  and posting (with or without images) to Bluesky using the provided client utilities.
  Methods
  -------
  __init__():
    Initializes the BlueskyManager instance and logs in using credentials from settings.
  build_text(title, content):
    Constructs a text builder object with the given title and content, separated by two newlines.
  create_post(text_builder, image: bytes = None):
    Creates a post on Bluesky using the provided text builder. If an image is provided, posts with the image; otherwise, posts text only.
  """
  def __init__(self):
    self.client = Client()
    self.client.login(
      settings.BLUESKY_HANDLE,
      settings.BLUESKY_PASSWORD,
    )

  def build_text(self, content: str):
    """
    Constructs a text builder object with the given title and content, separated by two newlines.
    Parameters
    ----------
    content : str
      The content of the post.
    Returns
    -------
    client_utils.TextBuilder
      A text builder object containing the formatted title and content.
    """
    text_builder = client_utils.TextBuilder()
    text_builder.text(content)
    return text_builder
  
  def create_post(self, text_builder: client_utils.TextBuilder, image: bytes = None):
    """
    Creates a post on Bluesky using the provided text builder. 
    If an image is provided, posts with the image; otherwise, posts text only.
    Parameters
    ----------
    text_builder : client_utils.TextBuilder
      The text builder object containing the formatted title and content.
    image : bytes, optional
      The image to be included in the post. If not provided, only text will be posted.
    Returns
    -------
    client_utils.Post
      The created post object.
    """
    if image:
      post = self.client.send_image(
        text=text_builder,
        image=image,
        image_alt=''
      )
    else:
      post = self.client.send_post(text_builder)
    return post

class TelegramManager:
  """
  TelegramManager provides an interface to interact with the Telegram messaging platform.
  This class handles sending messages and images to a specified chat using the Telegram Bot API.
  Methods
  -------
  __init__():
    Initializes the TelegramManager instance with the bot token and chat ID from settings.
  send_message(message, image_path=None):
    Sends a message to the specified chat. If an image path is provided, sends the image along with the message.
  """
  def __init__(self):
    self.bot_token = settings.TELEGRAM_BOT_TOKEN
    self.chat_id = settings.TELEGRAM_CHAT_ID
    self.base_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
    self.send_image_url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
  
  def send_message(self, message:str, image_path:str = None):
    """
    Sends a message to the specified chat. If an image path is provided, sends the image along with the message.
    Parameters
    ----------
    message : str
      The text content of the message.
    image_path : str, optional
      The path to the image to be included in the message. If not provided, only text will be sent.
    Returns
    -------
    dict
      The response from the Telegram API.
    Raises
    -------
    Exception
      If the request to the Telegram API fails, an exception is raised with the error message.
    """
    if image_path:
      with open(image_path, 'rb') as image_file:
        files = {'photo': image_file}
        params = {
          'chat_id': self.chat_id,
          'caption': message,
        }
        response = requests.post(self.send_image_url, params=params, files=files)
        if response.status_code == 200:
          return response.json()
        else:
          raise Exception(f"Error sending image: {response.status_code} - {response.text}")
    else:
      params = {
        'chat_id': self.chat_id,
        'text': message,
      }
      response = requests.get(self.base_url, params=params)
      if response.status_code == 200:
        return response.json()
      else:
        raise Exception(f"Error sending message: {response.status_code} - {response.text}")