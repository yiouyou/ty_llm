import os
import openai
from _config import _config

token = _config['openai']['token']['ty']
# print(token)
openai.api_key = token

try:
  #Make your OpenAI API request here
  response = openai.Completion.create(prompt="Hello world",
                                      model="text-davinci-003")
  _re = response.choices[0]['text']
  _clean = _re.replace("\n", "")
  print(_clean)
except openai.error.APIError as e:
  #Handle API error here, e.g. retry or log
  print(f"OpenAI API returned an API Error: {e}")
  pass
except openai.error.APIConnectionError as e:
  #Handle connection error here
  print(f"Failed to connect to OpenAI API: {e}")
  pass
except openai.error.RateLimitError as e:
  #Handle rate limit error (we recommend using exponential backoff)
  print(f"OpenAI API request exceeded rate limit: {e}")
  pass

