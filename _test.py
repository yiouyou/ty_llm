from _prompt import ignore, language_en, language_zh
from _prompt import role_work_SD, role_work_MJ, example_MJ, role_work_CFA, role_work_ASPECT, role_work_KID, example_KID
from _util import token_len, make_prompt, llm_openai_chat

tests = {
    'sd': [
        role_work_SD,
        '',
        'Now give me an original prompt for a creative artistic image of a cute cartoon baby is playing with a toy.',
        language_en
    ],
    'mj': [
        role_work_MJ,
        example_MJ,
        'Now give me an original prompt for a creative artistic image of a cute cartoon baby is playing with a toy.',
        language_en
    ],
    'cfa': [
        role_work_CFA,
        '',
        """Now please write a concise summary of the following stock research report: 三未信安(688489)

事件概述
2023年2月23日，三未信安发布2022年度业绩快报。2022年度公司实现营业总收入3.39亿元，同比增长25.51%；实现利润总额11,075.95万元，同比增长31.72%；实现归属于母公司所有者的净利润10,570.32万元，同比增长41.51%；实现归属于母公司所有者的扣除非经常性损益的净利润9,693.19万元，同比增长34.53%。

业绩符合预期，持续高增长
根据业绩快报，2022年度较2021年度公司营业利润、利润总额、归属于母公司所有者的净利润、归属于母公司所有者的扣除非经常性损益的净利润分别增长了30.92%、31.72%、41.51%和34.53%，其主要原因是公司产品化程度较高，营业收入增长超过成本增长，实现收入与利润的剪刀差。
根据业绩快报推测，公司Q4单季度实现营业收入1.67亿元，同比增长25.23%；归母净利润0.76亿元，同比增长31.55%；我们认为，22Q4在疫情影响的背景下，公司营业总收入、扣非净利润表现均有不俗表现。随着公司营收体量的增加，公司业绩有望持续高增长。
政策频出+国产化体系改造全面利好商密领域。
国产化体系改革势在必行，商密领域蓬勃发展，我们认为网络安全是国家的内生需求，我国密码产品中仍有较多产品使用国际定制的算法，存在不可控因素。软件端，随着密码法的实施，我国已经初步形成了自主可控的密码算法体系即SM体系。硬件端，随着国产芯片性能逐步提升，商用密码迎接国产化新机遇。
密评体系不断成熟，商密领域有望迎接以评促进新篇章，我国正处于密评试点的开展期阶段，试点力度和规模不断加大，未来密码有望打开以评促进的快速发展期。我们认为，公司的密码产品和硬件产品备受市场认可，在商密赛道蓬勃发展的大环境下有望大放异彩。

公司技术优势显著，密码芯片产品备受瞩目
商密领板卡:公司已经形成全面板卡业务体系满足多种业务场景，其中包括服务器、VPN、网关、可信计算、存储加密、云计算等，公司板卡综合各项指标整体处于行业先进水平。
密码机:公司密码机技术优势明显，符合多项行业认证，公司金融密码机通过美国联邦信息处理标准3级安全认证和国内安全等级三级认证。
密码芯片:公司自研芯片XS100支持多场景应用，可集成在密码板卡、密码整机、物联网终端、安全服务器等产品中使用。我们认为公司自研芯片有助于降本增效，有效提升核心产品的竞争力。未来，公司将密码算法优势固化在芯片，实现芯片级密码赋能，我们认为公司芯片有望借助物联网终端实现指数级别爆发式成长。

投资建议
根据公司业绩快报，我们下调公司22-24年营收预测3.75/5.17/6.86亿元至22-24年营收预测3.39/4.66/6.17亿元；下调22-24年每股收益（EPS）1.45/2.12/3.00元的预测，至22-24年分别为1.36/1.93/2.73元，对应2023年2月24日126.02元/股收盘价，PE分别为92.7/65.2/46.2倍，维持公司“买入”评级。

风险提示
疫情导致全球经济下行的风险，行业竞争加剧导致盈利水平下降，核心技术突破进程低于预期，公司核心人才团队流失风险，未经审计财报与最终财报可能存在差异。""",
        language_zh
    ],
    'aspect': [
        role_work_ASPECT,
        '',
        """这款产品不错，但电池不耐用。做它应该做的事情。它很轻，而且非常容易使用。很值这个钱。
我不喜欢这个产品，它很吵。总之，它很便宜。我吃的另一个更好。
完全按照它说的做。2天后到了这里，我对产品非常满意；）""",
        language_en
    ],
    'kid': [
        role_work_KID,
        example_KID,
        """Now give me several sets of children's puzzle questions generated from the following textual description of a cover image: 
"a baby with a monkey and cars in front of it on the beach with a gorilla"

These puzzle questions must be within one of categories: Color recognition, shape recognition, size comparison, emotion recognition, letters recognition, numbers recognition, common animal recognition, simple counting, or the ability to add and subtract within 10.
Each set of questions must be seperated by '----------'. No extra explanation.
""",
        language_en
    ],
}


for i in tests:
    _ignore = ignore
    _role_work = tests[i][0]
    _example = tests[i][1]
    _job = tests[i][2]
    _language = tests[i][3]
    _prompt = make_prompt()
    _txt = _prompt.format(_ignore = _ignore, _role_work = _role_work, _example = _example, _job = _job, _language = _language)
    # print(f"\n----------\n{_txt}\n----------\n")
    print(f"\n>>> {i} tokens: {token_len(_txt)}")
    _re = llm_openai_chat(0, _prompt, _ignore, _role_work, _example, _job, _language)
    print(f"<<<\n{_re}")

