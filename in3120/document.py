#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Dict, Any


class Document(ABC):
    """
    Abstract base class for a document. A document is a simple collection of
    named, typed fields.
    """

    def __getitem__(self, field_name: str) -> Any:
        return self.get_field(field_name, None)

    def __setitem__(self, field_name: str, field_value: Any) -> None:
        return self.set_field(field_name, field_value)

    @property
    def document_id(self) -> int:
        return self.get_document_id()

    @abstractmethod
    def get_document_id(self) -> int:
        """
        Returns the document's unique identifier.
        """
        pass

    @abstractmethod
    def get_field(self, field_name: str, default: Any) -> Any:
        """
        Returns the value of the named field in the document. If the document
        doesn't contain the named field, the provided default field value is
        returned instead.
        """
        pass

    @abstractmethod
    def set_field(self, field_name: str, field_value: Any) -> None:
        """
        Sets the named field in the document to the given value.
        """
        pass


class InMemoryDocument(Document):
    """
    A very simple and straightforward in-memory implementation of a document.
    Note that what we index are normalized versions of the raw fields. We keep
    the raw fields here in order to preserve the original presentation.
    """

    def __init__(self, document_id: int, fields: Dict[str, Any]):
        assert document_id is not None
        assert isinstance(fields, dict)
        self.__document_id = document_id
        self.__fields = fields

    def __repr__(self):
        return str({"document_id": self.__document_id, "fields": self.__fields})

    def get_document_id(self) -> int:
        return self.__document_id

    def get_field(self, field_name: str, default: Any) -> Any:
        return self.__fields.get(field_name, default)

    def set_field(self, field_name: str, field_value: Any) -> None:
        assert field_name is not None
        self.__fields[field_name] = field_value
