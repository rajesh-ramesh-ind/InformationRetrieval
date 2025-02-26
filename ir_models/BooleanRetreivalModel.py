# Boolean retrieval model
from typing import Any, List

from utils import *

from ir_models.base import IRModel
import re


def merge_postings(p1: List, p2: List, op: str) -> List:
    match op:
        case "OR":
            i, j = 0, 0
            res = []
            while i < len(p1) and j < len(p2):
                if p1[i] == p2[j]:
                    res.append(p1[i])
                    i += 1
                    j += 1
                elif p1[i] < p2[j]:
                    res.append(p1[i])
                    i += 1
                else:
                    res.append(p2[j])
                    j += 1
            res += p1[i:]
            res += p2[j:]
            return res
        case "AND":
            i, j = 0, 0
            res = []
            while i < len(p1) and j < len(p2):
                if p1[i] == p2[j]:
                    res.append(p1[i])
                    i += 1
                    j += 1
                elif p1[i] < p2[j]:
                    i += 1
                else:
                    j += 1
            return res
        case "NOT":
            return list(filter(lambda doc_id: doc_id not in p2, p1))


def tokenize(exp):
    return [t.strip() for t in re.sub(
        pattern=r"\(|\)| ?AND ?| ?NOT ?| ?OR ?",
        string=exp,
        repl=r"#\g<0>#"
    ).split("#") if t != ""]


class BooleanRetrievalModel(IRModel):
    total_docs = 0
    indexed_data: Dict[str, Dict] = {}

    def __init__(self):
        pass

    def index_docs(self, docs: List):
        self.total_docs = len(docs)
        self.indexed_data = build_inverted_index(
            docs,
            tokenizer=lambda x: x.split(" "),
            normalization=lambda x: "".join(filter(lambda y: y.isalnum(), x.lower()))
        )

    def query(self, q: str):
        tokens = tokenize(q)
        results = self.process_expression(tokens)
        return results

    def process_expression(self, tokenized_expression: List[str]) -> List:
        if len(tokenized_expression) == 0:
            return []
        elif len(tokenized_expression) == 1:
            return [self.indexed_data[tokenized_expression[0]]["postings"]]
        else:
            operands: List = []
            operators: List = []
            for token in tokenized_expression:
                token = token if token in ("AND", "OR", "NOT") else token.lower()
                match token:
                    case "AND" | "OR" | "NOT" | '(':
                        operators.append(token)
                    case ')':
                        op = operators.pop()
                        match op:
                            case "NOT":
                                res = self.merge_it_s(operands.pop(), op)
                                operands.append(res)
                            case _:
                                t2 = operands.pop()
                                t1 = operands.pop()
                                res = self.merge_it(t1, t2, op)
                                operands.append(res)
                                while operators[-1] != "(":
                                    operators.pop()
                                operators.pop()
                    case _:
                        operands.append(token)
            while len(operators) > 0:
                op = operators.pop()
                match op:
                    case "NOT":
                        res = self.merge_it_s(operands.pop(), op)
                        operands.append(res)
                    case _:
                        t2 = operands.pop()
                        t1 = operands.pop()
                        res = self.merge_it(t1, t2, op)
                        operands.append(res)
                        while len(operators) > 0 and operators[-1] != "(":
                            operators.pop()
            return operands

    def define_framework(self) -> Any:
        pass

    def scoring_function(self, query, document) -> float:
        pass

    def __parse_query(self, q):
        pass

    def search(self, term: str, docs: List, op: str) -> List:
        term_data: List = self.indexed_data[term]["postings"]
        return merge_postings(docs, term_data, op)

    def merge_it_s(self, p1, op) -> List:
        match p1:
            case str():
                return merge_postings(list(range(1, self.total_docs + 1)), self.indexed_data[p1]["postings"], op)
            case list():
                return p1
            case _:
                return list()

    def merge_it(self, p1, p2, op: str) -> List:
        match (p1, p2):
            case (str(), str()):
                return merge_postings(
                    self.indexed_data[p1]["postings"],
                    self.indexed_data[p2]["postings"],
                    op
                )
            case (list(), list()):
                return merge_postings(
                    p1, p2, op
                )
            case (str(), list()):
                return merge_postings(
                    self.indexed_data[p1]["postings"],
                    p2, op
                )
            case (list(), str()):
                return merge_postings(
                    p1,
                    self.indexed_data[p2]["postings"],
                    op
                )
            case _:
                return list()
