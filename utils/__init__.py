from typing import List, Callable, Dict, Tuple, NamedTuple


def prepare_term_document_incidence_matrix(
        docs: List[str],
        tokenizer: Callable[[str], List[str]]
) -> List[List[int]]:
    unique_words = set()
    tokenized_docs = list()
    for doc in docs:
        tokens = tokenizer(doc)
        unique_words.update(tokens)
        tokenized_docs.append(tokens)
    unique_words = sorted(unique_words)

    return [
        [
            1 if word in td else 0
            for word in unique_words
        ]
        for td in tokenized_docs
    ]


def group_by(token_doc_id_pairs: List[List[Tuple[str, int]]]):
    index: Dict[str, Dict] = dict()

    for docs_pair in token_doc_id_pairs:
        processed_tokens = set()
        for (term, doc_id) in docs_pair:
            if not term in processed_tokens:
                idx_ref_ = index.get(term)
                if not idx_ref_:
                    index[term] = {
                        "doc_freq": 1,
                        "postings": [doc_id]
                    }
                else:
                    idx_ref_["doc_freq"] += 1
                    idx_ref_["postings"].append(doc_id)
                processed_tokens.add(term)

    return index


def build_inverted_index(
        docs: List[str],
        tokenizer: Callable[[str], List[str]],
        normalization: Callable[[str], str]
) -> Dict[str, Dict]:
    tokenized_docs = [tokenizer(doc) for doc in docs]

    normalized_doc_tokens = [list(map(normalization, tokens)) for tokens in tokenized_docs]

    token_doc_id_pair = [[(token, doc_id + 1) for token in ndt] for doc_id, ndt in enumerate(normalized_doc_tokens)]
    token_doc_id_pair.sort(key=lambda tup: (tup[0], tup[1]))

    return group_by(token_doc_id_pair)


# inverted_index = build_inverted_index(
#     [
#         "I did enact Julius Caesar I was killed i' the Captiol; Brutus killed me.",
#         "So let it be with Caesar. the noble Brutus hath told you Caesar was ambitious"
#     ],
#     lambda x: x.split(" "),
#     lambda x: "".join(filter(lambda y: y.isalnum(), x.lower()))
# )
#
# from pprint import pprint
#
# pprint(inverted_index)
