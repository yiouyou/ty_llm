# python .\kid_prompt2img.py -dir ./test -ppromt 'a blue dog, cartoon style'
import os
import json
import argparse
from _util import sys_cmd, api_interrogate

parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-ppromt', action='store', help='ppromt', type=str, default='')
parser.add_argument('-dir', action='store', help='dir', type=str, default='./')
# parser.add_argument('-coverimg', action='store', help='coverimg', type=str, default='')
parser.add_argument('-scribbleimg', action='store', help='scribbleimg', type=str, default='')
options = parser.parse_args()
_ppromt = options.ppromt
_dir = options.dir
# _coverimg = options.coverimg
_scribbleimg = options.scribbleimg

p_promt = _ppromt
# _content, _style = api_interrogate(_coverimg)
# if _style:
#     p_promt = f"{_ppromt}, {_style}"

_txt_out_dir = _dir
_img_out_dir = _dir
_user_conf_json = os.path.join(_dir, 'tmp_1.json')

_json = {
    "user_+_prompt": p_promt,
    "user_-_prompt": "",
    "n_batch": 1,
    "creative": "中",
    "user_sys_conf": "出题",
    "user_imgs": {
        "草图": _scribbleimg,
    }
}

with open (_user_conf_json, "w", encoding='utf-8') as wjson:
    wjson.write(json.dumps(_json, indent=4, ensure_ascii=False))


cmd_ci_i2i = f"python _ci_i2i.py -txtoutdir {_txt_out_dir} -imgoutdir {_img_out_dir} -userconf {_user_conf_json}"
print(cmd_ci_i2i)
sys_cmd(cmd_ci_i2i)

