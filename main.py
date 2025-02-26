from ir_models.BooleanRetreivalModel import BooleanRetrievalModel

if __name__ == "__main__":
    docs = [
        "I did enact Julius Caesar I was killed i' the Captiol; Brutus killed me.",
        "So let it be with Caesar. the noble Brutus hath told you Caesar was ambitious"
    ]

    brm = BooleanRetrievalModel()

    brm.index_docs(docs)

    res = brm.query("I OR so")

    print(res)
