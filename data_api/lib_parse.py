import os
import re
import shutil
import subprocess
import tempfile
from subprocess import PIPE, STDOUT, Popen

from markdown2 import Markdown

from .deps import logger

# FIXME: Remove global variable
ITER = 0
MDOWNER = Markdown()


def txt2html(text):
    html_text = MDOWNER.convert(
        text.replace('_', '\\_')
    )
    html_text = convert(html_text)
    return html_text


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


def getLatexTemplate(name):
    lines = []
    path = '%s/../templates' % os.path.dirname(__file__)
    with open(f'{path}/{name}.tex', encoding='utf8') as f:
        for line in f:
            lines.append(line)
    return ''.join(lines)


def md2latex(data, template='default_doc'):
    # See http://www.practicallyefficient.com/2016/12/04/pandoc-and-python.html
    p = Popen(['pandoc', '-f', 'markdown', '-t', 'latex', '--wrap=preserve'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    latex_raw = p.communicate(input=str.encode(data.get('body', '')))[0]
    latex = latex_raw.decode()
    # remove \tightlist
    latex = re.sub(r'\\tightlist\n', r'', latex)
    # join \item with its text on a single line; also put tabs in front of \item
    latex = re.sub(r'\\item\n\s+', r'\t\\item ', latex)
    # remove all LaTeX labels
    latex = re.sub(r'\\label.*', r'', latex)

    # add page breaks
    latex = re.sub(r"-{4,}", '---', latex)
    latex = re.sub(r"---(.+?)---", r'\\vfill\1\\pagebreak\n\n', latex)

    mask = getLatexTemplate(template)
    # We use old string formatting, less troubles with latex format
    return mask % {
        'body': latex,
        'title': data.get('title', 'OpenJustice.be Document')
    }


def latex2pdf(latex):
    logger.debug('Starting latex 2 pdf, file size %s', len(latex))
    temp = tempfile.mkdtemp()
    wdir = os.getcwd()
    os.chdir(temp)

    f = open('file.tex', 'w')
    f.write(latex)
    f.close()

    proc = Popen(['pdflatex', '-interaction=batchmode', 'file.tex'])
    proc.communicate()

    rawFile = None
    with open('file.pdf', mode='rb') as f:
        rawFile = f.read()

    shutil.rmtree(temp)
    os.chdir(wdir)

    return rawFile
