# -*- coding: utf-8 -*-

from app import logging
from re import sub
import logging


def markup_multipurpose_fixes(source_text):
    try:
        source_text = escape_markdown(source_text)
    except Exception as e:
        logging.debug("Cannot perform escape markdown fixes in multipurpose markup fixes.")

    try:
        source_text = md_convert_links(source_text)
    except Exception as e:
        logging.debug("Cannot perform markdown convert links fixes in multipurpose markup fixes.")

    try:
        source_text = hts_splitting(source_text)
    except Exception as e:
        logging.debug("Cannot perform hashtags splitting fixes in multipurpose markup fixes.")

    try:
        return source_text.strip()
    except Exception as e:
        logging.debug("Cannot strip source text in multipurpose markup fixes.")


def md_convert_links(source_text):
    partitioned_text = source_text.partition('[')[-1].rpartition(']')[0]
    splitted_text = partitioned_text.split("]")
    for link in splitted_text:
        try:
            try:
                link = link.split("[")[1]
            except IndexError:
                pass
            link_splitted = link.split("|")
            replace_link = "\[" + str(link_splitted[0]) + "|" + str(link_splitted[1]) + "]".strip()
            response_link = "[" + str(link_splitted[0]) + "](https://" + str(link_splitted[1]) + ")".strip()
            source_text = source_text.replace(replace_link, response_link)
        except IndexError:
            continue

    return source_text


def escape_markdown(source_text):
    escape_chars = '\*_`\['

    return sub(r'([%s])' % escape_chars, r'\\\1', source_text)


def hts_splitting(source_text):
    splitted_text = {tag.strip("@") for tag in source_text.split() if tag.startswith("#")}
    listed_text = list(splitted_text)
    for ht_element in listed_text:
        splitted_text = ht_element.split("@")[0]
        source_text = source_text.replace(ht_element, splitted_text)

    return source_text
