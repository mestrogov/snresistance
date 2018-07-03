# -*- coding: utf-8 -*-

from re import sub


def markup_multipurpose_fixes(source_text):
    source_text = md_convert_links(source_text)
    source_text = hs_splitting(source_text)
    source_text = escape_markdown(source_text)

    return source_text


def md_convert_links(source_text):
    partitioned_text = source_text.partition('[')[-1].rpartition(']')[0]
    splitted_text = partitioned_text.split("]")
    for link in splitted_text:
        try:
            link = link.split("[")[1]
        except IndexError:
            pass
        link_splitted = link.split("|")
        replace_link = "[" + str(link_splitted[0]) + "|" + str(link_splitted[1]) + "]".strip()
        response_link = "[" + str(link_splitted[0]) + "](https://" + str(link_splitted[1]) + ")".strip()
        source_text = source_text.replace(replace_link, response_link)

    return source_text


def escape_markdown(source_text):
    escape_chars = '\*_`\['

    return sub(r'([%s])' % escape_chars, r'\\\1', source_text)


def hs_splitting(source_text):
    stripped_text = {tag.strip("@") for tag in source_text.split() if tag.startswith("#")}
    listed_text = list(stripped_text)
    for hs_element in listed_text:
        splitted_text = hs_element.split("@")[0]
        source_text = source_text.replace(hs_element, splitted_text)

    return source_text.strip()
