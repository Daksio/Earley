import pytest
import sys
sys.path.append('../src')
from earley import *

def test1():
    start = "S"
    terms = ["a", "b"]
    non_terms = ["S"]
    Rules = ["S->aSbS", "S->"]
    Parser = Earley()
    Parser.fit(start, terms, non_terms, Rules)
    first = ["aababb"]
    second = ["aabbba"]
    for i in first:
        if Parser.applyPredict(i) == 0:
            assert False
    for i in second:
        if Parser.applyPredict(i) == 1:
            assert False
    assert True


def test2():
    start = "S"
    terms = ["a", "b", "c", "d"]
    non_terms = ["S", "D", "C"]
    Rules = ["S->Sa", "S->C", "S->SSb", "C->Dd", "D->cD", "D->"]
    Parser = Earley()
    Parser.fit(start, terms, non_terms, Rules)
    first = ["cdcdba", "ccccd", "d"]
    second = ["cccdab", "c"]
    for i in first:
        if Parser.applyPredict(i) == 0:
            assert False
    for i in second:
        if Parser.applyPredict(i) == 1:
            assert False
    assert True
