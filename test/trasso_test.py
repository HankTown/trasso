# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 14:56:02 2019

@author: HankTown
"""

from trasso import extract
asso_result=extract.get_asso_words('rdbg2019.txt','stopwords.txt','习近平',m=20)
for w in asso_result:
    print(w)