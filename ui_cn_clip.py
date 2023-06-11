import gradio as gr
import os

from _prompt import ignore, language_en, language_zh
from _prompt import role_work_KID_img2puzzle, example_KID_img2puzzle
from _util import token_len, make_prompt, llm_openai_chat, api_interrogate




def get_file_path(file_path):
    return file_path


# def get_img_content(file_path):
#     _img_content = ""
#     if file_path:
#         _content, _style = api_interrogate(file_path)
#         _img_content = _content
#     return _img_content


# def caption_agent(_key, file_path):
#     _img_caption = ""
#     if _key:
#         from PIL import Image
#         from transformers.tools import OpenAiAgent
#         agent = OpenAiAgent(
#             model='text-davinci-003',
#             api_key=_key
#         )
#         if file_path:
#             _image = Image.open(file_path)
#             _img_caption = agent.run("can you caption the `image`?", image=_image)
#             print(_img_caption)
#     else:
#         _img_caption = "ERROR: Please input your OpenAI API Key first!"
#     return _img_caption


def clip_interrogator(file_path):
    _img_content = ""
    if file_path:
        from PIL import Image
        from clip_interrogator import Config, Interrogator
        image = Image.open(file_path).convert('RGB')
        ci = Interrogator(Config(clip_model_name="ViT-L-14/openai"))
        _caption = ci.interrogate(image)
        _s = _caption.split(', ')
        _content = _s[0]
        _style = ', '.join(_s[1:])
        _img_content = _content
        print(_img_content)
    return _img_content


def make_img_prompt(_img_content):
    _txt = ""
    _log = ""
    if _img_content:
        job_KID_img2puzzle = f"Now give me several sets of children's puzzle questions generated from the following textual description of a cover image: '{_img_content}'." + """

These puzzle questions must be within one of categories: Color recognition, shape recognition, size comparison, emotion recognition, letters recognition, numbers recognition, common animal recognition, simple counting, or the ability to add and subtract within 10.
Each set of questions must be seperated by '----------'. No extra explanation.
"""
        _prompt = make_prompt()
        _ignore = ignore
        _role_work = role_work_KID_img2puzzle
        _example = example_KID_img2puzzle
        _job = job_KID_img2puzzle
        _language = language_en
        _txt = _prompt.format(_ignore = _ignore, _role_work = _role_work, _example = _example, _job = _job, _language = _language)
        _log = f">>> prompt tokens: {token_len(_txt)}"
    return [_txt, _log]


def chg_btn_color_if_prompt(_img_prompt):
    if _img_prompt:
        return gr.update(variant="primary")
    else:
        return gr.update(variant="secondary")


def run_img2puzzles_llm(_key, _prompt):
    if _key and _prompt:
        return img2puzzles_llm(_key, _prompt)
    elif not _prompt and _key:
        return ["ERROR: Please upload a Image file first!", ""]
    elif not _key and _prompt:
        return ["ERROR: Please input your OpenAI API Key first!", ""]
    else:
        return ["ERROR: Please input your OpenAI API Key AND upload a Image file first!", ""]


def img2puzzles_llm(_key, _prompt):
    from langchain import PromptTemplate, LLMChain
    from langchain.chat_models import ChatOpenAI
    _log = ""
    _puzzles = ""
    os.environ["OPENAI_API_KEY"] = _key
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    chain = LLMChain(llm=llm, prompt=PromptTemplate.from_template("{input}"))
    _puzzles = chain.run(input=_prompt)
    if _puzzles:
        _log = "Succeed!"
    return [_puzzles, _log]



with gr.Blocks(title = "从封面图片生成益智题目集") as demo:
    gr.Markdown("## 从封面图片生成益智题目集")
    with gr.Tab(label = ""):
        with gr.Row():
            openai_api_key = gr.Textbox(label="OpenAI API Key", placeholder="sk-**********", lines=1)
        with gr.Row():
            with gr.Column(scale=1):
                upload_img = gr.Image(label="上传封面", source="upload", type="filepath", interactive=True)
            with gr.Column(scale=1):
                img_interrogate = gr.Textbox(label="封面解读", placeholder="Image Interrogate", lines=1, interactive=False, visible=True)
                # upload_img.change(get_img_content, inputs=[upload_img], outputs=[img_interrogate])
                # upload_img.change(caption_agent, inputs=[openai_api_key, upload_img], outputs=[img_interrogate])
                upload_img.change(clip_interrogator, inputs=[upload_img], outputs=[img_interrogate])
        # with gr.Row():
        #     with gr.Column(scale=1):
        #         img_filepath = gr.Textbox(label="Image File Path", placeholder="Image File Path", lines=1, interactive=False, visible=True)
        #         upload_img.change(get_file_path, inputs=[upload_img], outputs=[img_filepath])
        with gr.Row():
            with gr.Column(scale=3):
                img_prompt = gr.Textbox(label="封面提示词", placeholder="Image Prompt", lines=5, max_lines=5, interactive=False, visible=True)
            with gr.Column(scale=1):
                img_prompt_log = gr.Textbox(label="Prompt Log", placeholder="Prompt Log", lines=5, max_lines=5, interactive=False, visible=True)
                img_interrogate.change(make_img_prompt, inputs=[img_interrogate], outputs=[img_prompt, img_prompt_log])
        with gr.Row():
            start_btn = gr.Button("开始生成", variant="secondary")
            img_prompt.change(chg_btn_color_if_prompt, inputs=[img_prompt], outputs=[start_btn])
        with gr.Row():
            with gr.Column(scale=3):
                img_puzzles = gr.Textbox(label="益智题目集", placeholder="Image Puzzles", lines=5, max_lines=15, interactive=False, visible=True)
            with gr.Column(scale=1):
                img_puzzles_log = gr.Textbox(label="Puzzles Log", placeholder="Puzzles Log", lines=5, max_lines=15, interactive=False, visible=True)
                start_btn.click(run_img2puzzles_llm, inputs=[openai_api_key, img_prompt], outputs=[img_puzzles, img_puzzles_log])



# from fastapi import FastAPI, Response
# import json
# app = FastAPI()

# @app.get("/")
# def index():
#     return {"message": "Customer Sentiment Analysis by LLM"}

# app = gr.mount_gradio_app(app, demo, path="/ui")



if __name__ == "__main__":
    demo.queue(concurrency_count=1).launch()

