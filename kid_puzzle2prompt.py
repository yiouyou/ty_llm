# python .\kid_puzzle2prompt.py -puzzle 'Which crayon has the letter D on it?'
from _prompt import ignore, language_en, language_zh
from _prompt import role_work_KID_puzzle2prompt, example_KID_puzzle2prompt
from _util import token_len, make_prompt, llm_openai_chat

import argparse
parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-puzzle', action='store', help='puzzle', type=str, default="")
options = parser.parse_args()
_puzzle = options.puzzle



job_KID_puzzle2prompt = f"Now, according to the following question, generate two prompts for generating two question option pictures: '{_puzzle}'."


data = {
    'kid_puzzle2prompt': [
        role_work_KID_puzzle2prompt,
        example_KID_puzzle2prompt,
        job_KID_puzzle2prompt,
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

