# -*- coding: utf-8 -*-


def split_list(slist, size):
    rlist = []
    while len(slist) > size:
        lpart = slist[:size]
        rlist.append(lpart)
        slist = slist[size:]
    rlist.append(slist)
    return rlist
