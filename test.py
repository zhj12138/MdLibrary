import markdown
from bs4 import BeautifulSoup

with open('Javascript-1.md', 'r', encoding='utf-8') as f:
    text = f.read()

extensions = [
        'markdown.extensions.abbr',
        'markdown.extensions.attr_list',
        'markdown.extensions.def_list',
        'markdown.extensions.fenced_code',
        'markdown.extensions.footnotes',
        'markdown.extensions.md_in_html',
        'markdown.extensions.tables',
        'markdown.extensions.codehilite',
        'markdown.extensions.legacy_em',
        'markdown.extensions.toc',
        'markdown.extensions.wikilinks',
        'markdown.extensions.admonition',
        'markdown.extensions.legacy_attrs',
        'markdown.extensions.meta',
        'markdown.extensions.nl2br',
        'markdown.extensions.sane_lists',
        'markdown.extensions.smarty',
]
html = markdown.markdown(text, extensions=extensions)
# print(html)
soup = BeautifulSoup(html, 'html.parser')
a = soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
print([[line.name,  line.text] for line in a])
# a = soup.find(['h1'])
# t = a[0]
# for line in a:
#     print(line)
#     print(line.name)
#     print(type(line.name))



