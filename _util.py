import os
import json
import tiktoken
from langchain import PromptTemplate, LLMChain
from langchain.chat_models import ChatOpenAI
from _config import _config
import io
import time
import base64
import requests
import subprocess
from PIL import Image



# | Encoder | Models |
# | --- | --- |
# | `cl100k_base` | `gpt-4`, `gpt-3.5-turbo`, `text-embedding-ada-002` |
# | `p50k_base` | `text-davinci-003`, `code-davinci-002`, `code-cushman-002` |
# | `r50k_base` | `text-davinci-001`, `davinci`, `text-similarity-davinci-001` |
# | `gpt2` | `gpt2` |
def token_len(text):
    tokenizer = tiktoken.get_encoding('cl100k_base')
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)


def make_prompt():
    template = """{_ignore}
{_role_work}
{_example}
{_job}
{_language}"""
    _prompt = PromptTemplate(
        input_variables=["_ignore", "_role_work", "_example", "_job", "_language"],
        template=template)
    return _prompt


def llm_openai_chat(_temperature, _prompt, _ignore, _role_work, _example, _job, _language):
    os.environ["OPENAI_API_KEY"] = _config['openai']['token']['ty']
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=_temperature)
    chain = LLMChain(llm=llm, prompt=_prompt)
    input = {
        "_ignore": _ignore,
        "_role_work": _role_work,
        "_example": _example,
        "_job": _job,
        "_language": _language,
    }
    _re = chain.run(input)
    # print(f"<<<\n{_re}")
    return _re


def api_interrogate(img_fn):
    _content = ''
    _style = ''
    if os.path.exists(img_fn):
        url = "http://127.0.0.1:12345"
        _url = f'{url}/sdapi/v1/interrogate'
        _payload = {
            "image": b64_img(img_fn),
            "model": "clip"
        }
        req = requests.post(url=_url, json=_payload)
        if req.status_code == 200:
            req_json = req.json()
            _caption = req_json['caption']
            if _caption:
                _s = _caption.split(', ')
                _content = _s[0]
                _style = ', '.join(_s[1:])
        # print(f'content: {_content}\nstyle: {_style}')
    return _content, _style


def b64_img(img_fn):
    img = Image.open(img_fn)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = 'data:image/png;base64,' + str(base64.b64encode(buffered.getvalue()), 'utf-8')
    return img_base64


def sys_cmd(_str):
    st = time.time()
    _out = subprocess.getoutput(_str)
    time.sleep(1)
    et = time.time()
    dt = et -st
    dt_fmt = time.strftime("%H:%M:%S", time.gmtime(dt))
    print(f"\n{_out}\n<<< {dt_fmt}")

