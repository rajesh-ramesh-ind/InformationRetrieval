from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IRModel(ABC):
    documents = []

    @abstractmethod
    def define_framework(self) -> Any:
        """
        Define the framework for modeling document and query representations and their relationships.
        This method should be implemented by subclasses.
        """
        pass

    @abstractmethod
    def scoring_function(self, query, document) -> float:
        """
        Assign a real number to a query and a document based on their representations.
        This method should be implemented by subclasses.
        """
        pass

    def rank_documents(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank documents based on the scoring function for a given query.
        """
        scored_documents = [(document, self.scoring_function(query, document)) for document in self.documents]
        ranked_documents = sorted(scored_documents, key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked_documents]

    @abstractmethod
    def index_docs(self, docs): pass

    @abstractmethod
    def query(self, q: str): pass
