#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations
from abc import abstractmethod
from ast import Call
from typing import Any, List, Dict, Callable
import collections.abc
from .document import Document, InMemoryDocument
from .documentpipeline import DocumentPipeline


class Corpus(collections.abc.Iterable):
    """
    Abstract base class representing a corpus we can index and search over,
    i.e., a collection of documents. The class facilitates iterating over
    all documents in the corpus.
    """

    def __len__(self):
        return self.size()

    def __getitem__(self, document_id: int) -> Document:
        return self.get_document(document_id)

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def size(self) -> int:
        """
        Returns the size of the corpus, i.e., the number of documents in the
        document collection.
        """
        pass

    @abstractmethod
    def get_document(self, document_id: int) -> Document:
        """
        Returns the document associated with the given document identifier.
        """
        pass


class InMemoryCorpus(Corpus):
    """
    An in-memory implementation of a document store, suitable only for small
    document collections.

    Document identifiers are assigned on a first-come first-serve basis.
    """

    def __init__(self, filename: str = None, pipeline: DocumentPipeline = None):
        self._documents = []
        pipeline = DocumentPipeline([]) if pipeline is None else pipeline
        if filename:
            if filename.endswith(".txt"):
                self.__load_text(filename, pipeline)
            elif filename.endswith(".xml"):
                self.__load_xml(filename, pipeline)
            elif filename.endswith(".json"):
                self.__load_json(filename, pipeline)
            elif filename.endswith(".csv"):
                self.__load_csv(filename, pipeline)
            else:
                raise IOError("Unsupported extension")

    def __iter__(self):
        return iter(self._documents)

    def size(self) -> int:
        return len(self._documents)

    def get_document(self, document_id: int) -> Document:
        assert 0 <= document_id < len(self._documents)
        return self._documents[document_id]

    def add_document(self, document: Document, strict: bool = True) -> InMemoryCorpus:
        """
        Adds the given document to the corpus. Facilitates testing.
        """
        assert document is not None
        assert (not strict) or (document.document_id == len(self._documents))
        self._documents.append(document)
        return self

    def split(self, field_name: str, splitter: Callable[[Any], List[Any]] = None) -> Dict[Any, InMemoryCorpus]:
        """
        Divides the corpus up into multiple corpora, according to the value(s) of the
        named field. I.e.,, splits the corpus up into several smaller corpora.

        The value(s) of the named fields are used as keys for the splits. A custom splitter
        function can optionally be provided, in case the named field is multi-valued and/or the
        value(s) should be filtered or transformed in some way.
        """
        splitter = splitter if splitter else lambda v: [v]
        splits = {}
        for document in self:
            values = splitter(document.get_field(field_name, ""))
            for value in values:
                if value not in splits:
                    splits[value] = InMemoryCorpus()
                splits[value].add_document(document, False)
        return splits

    def __load_text(self, filename: str, pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given UTF-8 encoded text file. One document per line,
        tab-separated fields. Empty lines are ignored. The first field gets named "body",
        the second field (optional) gets named "meta". All other fields are currently ignored.
        """
        document_id = 0
        with open(filename, mode="r", encoding="utf-8") as f:
            for line in f:
                anonymous_fields = line.strip().split("\t")
                if len(anonymous_fields) == 1 and not anonymous_fields[0]:
                    continue
                named_fields = {"body": anonymous_fields[0]}
                if len(anonymous_fields) >= 2:
                    named_fields["meta"] = anonymous_fields[1]
                document = pipeline(InMemoryDocument(document_id, named_fields))
                if document:
                    self.add_document(document)
                    document_id += 1

    def __load_xml(self, filename: str, pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given XML file. The schema is assumed to be
        simple <doc> nodes. Each <doc> node gets mapped to a single document field
        named "body".
        """
        from xml.dom.minidom import parse

        def __get_text(nodes):
            data = []
            for node in nodes:
                if node.nodeType == node.TEXT_NODE:
                    data.append(node.data)
            return " ".join(data)

        dom = parse(filename)
        document_id = 0
        for body in [__get_text(n.childNodes) for n in dom.getElementsByTagName("doc")]:
            document = pipeline(InMemoryDocument(document_id, {"body": body}))
            if document:
                self.add_document(document)
                document_id += 1

    def __load_csv(self, filename: str, pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given UTF-8 encoded CSV file. One document per line.
        """
        import csv

        document_id = 0
        with open(filename, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                document = pipeline(InMemoryDocument(document_id, dict(row)))
                if document:
                    self.add_document(document)
                    document_id += 1

    def __load_json(self, filename: str, pipeline: DocumentPipeline) -> None:
        """
        Loads documents from the given UTF-8 encoded JSON file. One document per line.
        Lines that do not start with "{" are ignored.
        """
        from json import loads

        document_id = 0
        with open(filename, mode="r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("{"):
                    named_fields = loads(line)
                    document = pipeline(InMemoryDocument(document_id, named_fields))
                    if document:
                        self.add_document(document)
                        document_id += 1
