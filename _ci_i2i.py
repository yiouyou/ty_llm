# python37 ci-i2i-202303.py -txtoutdir ./ -imgoutdir ./ -userconf ./ci-i2i-user.json

import json
from PIL import Image
from pprint import pprint
import os
import random
import time
import calendar
import argparse
from _ci_i2i_util import api_upscale, api_reload_model, api_interrogate
from _ci_i2i_util import api_i2i, api_i2i_ctrl, api_t2i, api_t2i_ctrl
from _ci_i2i_util import parse_creative, parse_sd1x_lora, parse_ctrl_units
from _ci_i2i_util import b64_img, is_human, random_human, merge_prompt
from _ci_i2i_util import create_caption_txt, read_txt, create_blank_png


_i2i_sys_conf = ['联想', '萌宠']
_i2i_sys_conf_xg = ['线稿']
_i2i_sys_conf_fg = ['风格']
_i2i_sys_conf_bj = ['布局']
_i2i_sys_conf_lk = ['轮廓']
# _i2i_sys_conf_bjlk = ['布局轮廓']

_t2i_sys_conf_txt = ['文本']
_t2i_sys_conf_txtimg = ['图文']
_t2i_sys_conf_ip_act = ['考拉', '蓝熊']
_t2i_sys_conf_kid = ['出题']

_img_x = {
    '内容': 'content',
    '风格': 'style',
    '布局': 'depth',
    '轮廓': 'hed',
    '细节': 'canny',
    '草图': 'scribble',
    '配色': 'color',
    '法线': 'normal_map',
    '分割图': 'segmentation',
    '人物姿势': 'openpose'
}

parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-userconf', action='store', help='userconf', type=str, default='')
parser.add_argument('-txtoutdir', action='store', help='txtoutdir', type=str, default='')
parser.add_argument('-imgoutdir', action='store', help='imgoutdir', type=str, default='')
options = parser.parse_args()
_userconf = options.userconf
_txtoutdir = options.txtoutdir
_imgoutdir = options.imgoutdir

txt_out_dir = _txtoutdir
img_out_dir = _imgoutdir
os.makedirs(txt_out_dir, exist_ok=True)
os.makedirs(img_out_dir, exist_ok=True)
with open(_userconf) as usercf:
    usercf_json = usercf.read()
userconf_json = json.loads(usercf_json)
# print(userconf_json)
user_sys_conf = userconf_json['user_sys_conf']
if user_sys_conf in _t2i_sys_conf_ip_act:
    _sysconf = f"ci-i2i-sys-ip-{user_sys_conf}.json"
else:
    _sysconf = f"ci-i2i-sys-{user_sys_conf}.json"
if not os.path.exists(_sysconf):
    print(f"ERROR: {_sysconf} is not exists!")
    exit()
print(f"{_txtoutdir}, {_imgoutdir}, {_userconf}, {_sysconf}")

with open(_sysconf) as syscf:
    syscf_json = syscf.read()
sysconf_json = json.loads(syscf_json)
# print(sysconf_json)

user_pos_prompt = userconf_json['user_+_prompt']
user_neg_prompt = userconf_json['user_-_prompt']
n_batch = userconf_json['n_batch']
creative = userconf_json['creative']
user_imgs = userconf_json['user_imgs']

sys_payload = sysconf_json['basic_payload']
sys_pos_prompt = sysconf_json['pre_+_prompt']
sys_neg_prompt = sysconf_json['pre_-_prompt']
models_sd1x = sysconf_json['models_sd1x']
models_sd2x = sysconf_json['models_sd2x']
models_sd1x_lora = sysconf_json['models_sd1x_lora']
t2i_width = sysconf_json['t2i_width']
t2i_height = sysconf_json['t2i_height']


_payload = parse_creative(creative, sys_payload)
# pprint(_payload)

_pos_prompt = merge_prompt(sys_pos_prompt, user_pos_prompt)
_neg_prompt = merge_prompt(sys_neg_prompt, user_neg_prompt)


human = ["human", "people", "baby", "babies",
         "kid", "kids", "child", "children",
         "girl", "girls", "boy", "boys",
         "man", "men", "woman", "women"]
# race = ["caucasian", "black", "american indian", "latino", "asian"]
race = ["caucasian", "blone", "white", "black"]

_ctrl_net = ['style', 'depth', 'hed',
             'canny', 'scribble', 'color',
             'normal_map', 'segmentation', 'openpose']
_ctrl_net_high_denoising_strength = ['openpose']
_high_denoising_strength = 0.99



def user_t2i(model_key, _parm):
    pos_prompt = merge_prompt(_pos_prompt, _parm['caption'])
    neg_prompt = _neg_prompt
    if _parm['if_sd15']:
        prompt_sd1x = models_sd1x[model_key][1]
        prompt_sd1x_lora = parse_sd1x_lora(models_sd1x_lora)
        if prompt_sd1x:
            pos_prompt += f", {prompt_sd1x}"
        if prompt_sd1x_lora:
            pos_prompt += f", {prompt_sd1x_lora}"
    if is_human(pos_prompt, human):
        pos_prompt = random_human(pos_prompt, human, race)
        restore_faces = True
    else:
        restore_faces = False
    # override_settings["CLIP_stop_at_last_layers"] = 2
    override_settings = {}
    _add = {
        "prompt":  pos_prompt,
        "negative_prompt": neg_prompt,
        "width": _parm['width'],
        "height": _parm['height'],
        "seed": _parm['seed'],
        "restore_faces": restore_faces,
        "override_settings": override_settings,
    }
    _payload.update(_add)
    _hr = {
        "enable_hr": False,
        "hr_scale": 2,
        "hr_upscaler": "Latent",
    }
    _payload.update(_hr)
    _alwayson_scripts = {
        "alwayson_scripts": {
            "Composable Lora": { "args": [True, False, False] },
            "Latent Couple extension": { "args": [True, "1:1,1:2,1:2", "0:0,0:0,0:1", "0.2,0.8,0.8", 20] },
        },
    }
    ##### if 'AND' in prompt, activate 'Composable Lora' and 'Latent Couple extension'
    if "\nAND " in pos_prompt:
        _payload.update(_alwayson_scripts)
    _out = f"{_parm['pre_out']}_{model_key}_{_parm['nth']}_{_parm['ts']}_t2i"
    api_t2i(_payload, _out, _parm['model_name'])
    ##### rename out to upload
    out_png = f"{_out}_ignore.png"
    upload_png = f"{_out}.png"
    if os.path.exists(out_png):
        os.rename(out_png, upload_png)
        print(f"rename to {upload_png}")


def user_t2i_ctrl(model_key, _parm, _ctrls):
    pos_prompt = merge_prompt(_pos_prompt, _parm['caption'])
    neg_prompt = _neg_prompt
    if _parm['if_sd15']:
        prompt_sd1x = models_sd1x[model_key][1]
        prompt_sd1x_lora = parse_sd1x_lora(models_sd1x_lora)
        if prompt_sd1x:
            pos_prompt += f", {prompt_sd1x}"
        if prompt_sd1x_lora:
            pos_prompt += f", {prompt_sd1x_lora}"
    if is_human(pos_prompt, human):
        pos_prompt = random_human(pos_prompt, human, race)
        restore_faces = True
    else:
        restore_faces = False
    # override_settings["CLIP_stop_at_last_layers"] = 2
    override_settings = {}
    controlnet_units = parse_ctrl_units(_ctrls, user_sys_conf)
    # pprint(controlnet_units)
    _add = {
        "prompt":  pos_prompt,
        "negative_prompt": neg_prompt,
        "width": _parm['width'],
        "height": _parm['height'],
        "seed": _parm['seed'],
        "restore_faces": restore_faces,
        "override_settings": override_settings,
        "alwayson_scripts": {},
        "controlnet_units": controlnet_units,
    }
    _payload.update(_add)
    _out = f"{_parm['pre_out']}_{model_key}_{_parm['nth']}_{_parm['ts']}_t2i_ctrl"
    api_t2i_ctrl(_payload, _out, _parm['model_name'])
    ##### rename out to upload
    out_png = f"{_out}_ignore.png"
    upload_png = f"{_out}.png"
    if os.path.exists(out_png):
        os.rename(out_png, upload_png)
        print(f"rename to {upload_png}")


def user_i2i(model_key, _imgs, _parm):
    pos_prompt = merge_prompt(_pos_prompt, _parm['caption'])
    neg_prompt = _neg_prompt
    if _parm['if_sd15']:
        prompt_sd1x = models_sd1x[model_key][1]
        prompt_sd1x_lora = parse_sd1x_lora(models_sd1x_lora)
        if prompt_sd1x:
            pos_prompt += f", {prompt_sd1x}"
        if prompt_sd1x_lora:
            pos_prompt += f", {prompt_sd1x_lora}"
    if is_human(pos_prompt, human):
        pos_prompt = random_human(pos_prompt, human, race)
        restore_faces = True
    else:
        restore_faces = False
    # override_settings["CLIP_stop_at_last_layers"] = 2
    override_settings = {}
    _add = {
        "include_init_images": True,
        "init_images": [b64_img(_imgs['content'])],
        "prompt":  pos_prompt,
        "negative_prompt": neg_prompt,
        "width": _parm['width'],
        "height": _parm['height'],
        "seed": _parm['seed'],
        "restore_faces": restore_faces,
        "override_settings": override_settings,
    }
    _payload.update(_add)
    _out = f"{_parm['pre_out']}_{model_key}_{_parm['nth']}_{_parm['ts']}_i2i"
    api_i2i(_payload, _out, _parm['model_name'])
    ##### rename out to upload
    out_png = f"{_out}_ignore.png"
    upload_png = f"{_out}.png"
    if os.path.exists(out_png):
        os.rename(out_png, upload_png)
        print(f"rename to {upload_png}")


def user_i2i_ctrl(model_key, _imgs, _parm, _ctrls):
    pos_prompt = merge_prompt(_pos_prompt, _parm['caption'])
    neg_prompt = _neg_prompt
    if _parm['if_sd15']:
        prompt_sd1x = models_sd1x[model_key][1]
        prompt_sd1x_lora = parse_sd1x_lora(models_sd1x_lora)
        if prompt_sd1x:
            pos_prompt += f", {prompt_sd1x}"
        if prompt_sd1x_lora:
            pos_prompt += f", {prompt_sd1x_lora}"
    if is_human(pos_prompt, human):
        pos_prompt = random_human(pos_prompt, human, race)
        restore_faces = True
    else:
        restore_faces = False
    # override_settings["CLIP_stop_at_last_layers"] = 2
    override_settings = {}
    controlnet_units = parse_ctrl_units(_ctrls, user_sys_conf)
    # pprint(controlnet_units)
    _add = {
        "include_init_images": True,
        "init_images": [b64_img(_imgs['content'])],
        "prompt":  pos_prompt,
        "negative_prompt": neg_prompt,
        "width": _parm['width'],
        "height": _parm['height'],
        "seed": _parm['seed'],
        "restore_faces": restore_faces,
        "override_settings": override_settings,
        "alwayson_scripts": {},
        "controlnet_units": controlnet_units,
    }
    _payload.update(_add)
    _out = f"{_parm['pre_out']}_{model_key}_{_parm['nth']}_{_parm['ts']}_i2i_ctrl"
    for i in _ctrl_net_high_denoising_strength:
        if i in _ctrls.keys():
            if _payload['denoising_strength'] < _high_denoising_strength:
                _payload['denoising_strength'] = _high_denoising_strength
    # pprint(_payload)
    api_i2i_ctrl(_payload, _out, _parm['model_name'])
    out_png = f"{_out}_ignore.png"
    upload_png = f"{_out}.png"
    ##### upscale 4x and delete
    if user_sys_conf in _i2i_sys_conf_xg:
        if os.path.exists(out_png):
            api_upscale(out_png, upload_png)
            os.remove(out_png)
            print(f"delete {out_png}")
        blank_png = f"{_parm['pre_out']}_blank_ignore.png"
        if os.path.exists(blank_png):
            os.remove(blank_png)
            print(f"delete {blank_png}")
    else:
        ##### rename out to upload
        if os.path.exists(out_png):
            os.rename(out_png, upload_png)
            print(f"rename to {upload_png}")


def run(model_key, model, _imgs, _parm):
    model_name = model[0]
    model_trigger = model[1]
    print(f"{model_key}, {model_name}, '{model_trigger}'")
    _new, _hash = api_reload_model(model_name)
    # prLightPurple(f'model name: {_new}')
    # prLightPurple(f'model hash: {_hash[:10]}')
    print(f'model name: {_new}')
    print(f'model hash: {_hash[:10]}')
    for i in range(_parm['n_batch']):
        i_seed = int(random.randrange(4294967294))
        i_0 = str(i).zfill(2)
        _parm['seed'] = i_seed
        _parm['nth'] = i_0
        _parm['model_name'] = model_name
        if _imgs['content']:
            print(f"{_imgs['content']} {_parm['width']}*{_parm['height']}, {_parm['seed']}, {_parm['pre_out']}_{model_key}_{_parm['nth']}_{_parm['ts']}")
        else:
            print(f"NOIMG {_parm['width']}*{_parm['height']}, {_parm['seed']}, {_parm['pre_out']}_{model_key}_{_parm['nth']}_{_parm['ts']}")
        run_which(model_key, _imgs, _parm)


def run_which(model_key, _imgs, _parm):
    _ctrls = {}
    for i_ctrl in _ctrl_net:
        if _imgs[i_ctrl]:
            _ctrls[i_ctrl] = _imgs[i_ctrl]
    if _ctrls:
        print("_ctrls is NOT empty")
    else:
        print("_ctrls is empty")
    if _imgs['content']:
        if user_sys_conf in _i2i_sys_conf:
            if _ctrls:
                user_i2i_ctrl(model_key, _imgs, _parm, _ctrls)
            else:
                user_i2i(model_key, _imgs, _parm)
        elif user_sys_conf in _i2i_sys_conf_bj:
            ##### set depth as content
            _ctrls = {}
            _ctrls['depth'] = _imgs['content']
            _parm['caption'] = ''
            user_i2i_ctrl(model_key, _imgs, _parm, _ctrls)
        elif user_sys_conf in _i2i_sys_conf_lk:
            ##### set hed as content
            _ctrls = {}
            _ctrls['hed'] = _imgs['content']
            _parm['caption'] = ''
            user_i2i_ctrl(model_key, _imgs, _parm, _ctrls)
        # elif user_sys_conf in _i2i_sys_conf_bjlk:
        #     ##### set hed as content
        #     _ctrls = {}
        #     _ctrls['depth'] = _imgs['content']
        #     _ctrls['hed'] = _imgs['content']
        #     _parm['caption'] = ''
        #     user_i2i_ctrl(model_key, _imgs, _parm, _ctrls)
        elif user_sys_conf in _i2i_sys_conf_xg:
            ##### set hed as content
            _ctrls = {}
            _ctrls['hed'] = _imgs['content']
            ##### create blank.jpg
            _blank_png = f"{_parm['pre_out']}_blank_ignore.png"
            create_blank_png(_parm['width'], _parm['height'], _blank_png)
            print(f"create blank png for 线稿: {_blank_png}")
            ##### set content as blank.png
            _imgs['content'] = _blank_png
            ##### set caption as empty
            _parm['caption'] = ''
            user_i2i_ctrl(model_key, _imgs, _parm, _ctrls)
        elif user_sys_conf in _i2i_sys_conf_fg:
            if _imgs['style']:
                ##### set canny as content
                _ctrls = {}
                _ctrls['style'] = _imgs['style']
                _ctrls['canny'] = _imgs['content']
                # _content, _style = api_interrogate(_imgs['style'])
                _parm['caption'] = ''
                print(_ctrls)
                user_i2i_ctrl(model_key, _imgs, _parm, _ctrls)
            else:
                print(f"ERROR: for i2i, {user_sys_conf} doesn't have STYLE input!")
        else:
            print(f"ERROR: for i2i, {user_sys_conf} is not allowed!")
    else:
        if user_sys_conf in _t2i_sys_conf_txt:
            if _ctrls:
                print(f"ERROR: for t2i_txt, {user_sys_conf} shouldn't have ctrl input: {_ctrls}!")
            else:
                user_t2i(model_key, _parm)
        elif user_sys_conf in _t2i_sys_conf_txtimg:
            if _imgs['scribble']:
                user_t2i_ctrl(model_key, _parm, _ctrls)
            else:
                print(f"ERROR: for t2i_txtimg, {user_sys_conf} must have scribble input!")
        elif user_sys_conf in _t2i_sys_conf_ip_act:
            if _imgs['scribble']:
                ##### 与草图大小一致
                scribble_content = Image.open(_imgs['scribble'])
                _width, _height = scribble_content.size
                _parm['width'] = _width
                _parm['width'] = _height
                user_t2i_ctrl(model_key, _parm, _ctrls)
            else:
                print(f"ERROR: for t2i_ip, {user_sys_conf} must have scribble input!")
        elif user_sys_conf in _t2i_sys_conf_kid:
            if _imgs['scribble']:
                #### 与草图大小一致
                scribble_content = Image.open(_imgs['scribble'])
                _width, _height = scribble_content.size
                _parm['width'] = _width
                _parm['width'] = _height
            user_t2i_ctrl(model_key, _parm, _ctrls)
        else:
            print(f"ERROR: for t2i, {user_sys_conf} is not allowed!")


if os.path.exists(_userconf):

    ##### if 30-jpg-1679471675145522255.jpg
    _dir = _userconf.replace(os.path.basename(_userconf), '')
    ##### if 2023-03-22/30-jpg-1679471675145522255.jpg
    # _dir = "F:\\_workflow\\tmp\\input\\ci-i2i"
    # print(_dir)

    _imgs = {}
    for i in _img_x.keys():
        if i in user_imgs.keys():
            if user_imgs[i]:
                i_user_imgs = os.path.join(_dir, user_imgs[i])
                if os.path.exists(i_user_imgs):
                    _imgs[_img_x[i]] = i_user_imgs
                else:
                    print(f"ERROR: {i_user_imgs} doesn't exist!")
                    exit()                    
            else:
                _imgs[_img_x[i]] = ''
        else:
            _imgs[_img_x[i]] = ''
    # pprint(_imgs)

    _width = t2i_width
    _height = t2i_height
    _caption = ''
    _pre_out = os.path.join(img_out_dir, '')
    left, right = os.path.splitext(os.path.basename(_userconf))
    if _imgs['content']:
        ##### write caption
        caption_txt = os.path.join(txt_out_dir, f"{left}_caption.txt")
        _caption = create_caption_txt(_imgs['content'], caption_txt)
        ##### prepare parm
        _pre_out = os.path.join(img_out_dir, f"{left}")
        img_content = Image.open(_imgs['content'])
        _width, _height = img_content.size
    else:
        # _pre_out = os.path.join(img_out_dir, "txt")
        _pre_out = os.path.join(img_out_dir, f"{left}")
    parm = {}
    parm['n_batch'] = n_batch
    parm['caption'] = _caption
    parm['pre_out'] = _pre_out
    parm['width'] = _width
    parm['height'] = _height

    ##### run by models
    for i in models_sd1x:
        current_GMT = time.gmtime()
        ts = calendar.timegm(current_GMT)
        parm['ts'] = ts
        parm['if_sd15'] = 1
        run(i, models_sd1x[i], _imgs, parm)

    for i in models_sd2x:
        current_GMT = time.gmtime()
        ts = calendar.timegm(current_GMT)
        parm['ts'] = ts
        parm['if_sd15'] = 0
        run(i, models_sd2x[i], _imgs, parm)

