# python .\kid_img2puzzle.py -img covers/puzzle_cover.jpeg
from _prompt import ignore, language_en, language_zh
from _prompt import role_work_KID_img2puzzle, example_KID_img2puzzle
from _util import token_len, make_prompt, llm_openai_chat, api_interrogate

import argparse
parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-img', action='store', help='img', type=str, default="./puzzle_cover.jpeg")
options = parser.parse_args()
_img = options.img

_content, _style = api_interrogate(_img)
_cover_img_desc = _content # "a baby with a monkey and cars in front of it on the beach with a gorilla"
print(f"\ncover img desc: {_cover_img_desc}")


job_KID_img2puzzle = f"Now give me several sets of children's puzzle questions generated from the following textual description of a cover image: '{_cover_img_desc}'." + """

These puzzle questions must be within one of categories: Color recognition, shape recognition, size comparison, emotion recognition, letters recognition, numbers recognition, common animal recognition, simple counting, or the ability to add and subtract within 10.
Each set of questions must be seperated by '----------'. No extra explanation.
"""


data = {
    'kid_img2puzzle': [
        role_work_KID_img2puzzle,
        example_KID_img2puzzle,
        job_KID_img2puzzle,
        language_en
    ],
}


for i in data:
    _ignore = ignore
    _role_work = data[i][0]
    _example = data[i][1]
    _job = data[i][2]
    _language = data[i][3]
    _prompt = make_prompt()
    _txt = _prompt.format(_ignore = _ignore, _role_work = _role_work, _example = _example, _job = _job, _language = _language)
    print(f"\n----------\n{_txt}\n----------\n")
    print(f"\n>>> {i} tokens: {token_len(_txt)}")
    _re = llm_openai_chat(0, _prompt, _ignore, _role_work, _example, _job, _language)
    print(f"<<<\n{_re}")

