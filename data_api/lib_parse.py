import re
# FIXME: Remove global variable
ITER = 0


def convert(text):
    text = page_breaks(text)
    return text


def repl(match):
    global ITER
    group = match.group(1)
    out = f'<a name="p{ITER}"></a><div class="page_bar"><a href="#p{ITER}">{group}</a></div>'
    ITER = ITER + 1
    return out


def page_breaks(text):
    global ITER
    # text = re.sub(r"---(.*?)---", r'<div class="page_bar">\1</div>', text)
    ITER = 1
    text = re.sub(r"-{4,}", '---', text)
    text = re.sub(r"---(.+?)---", repl, text)
    return text
