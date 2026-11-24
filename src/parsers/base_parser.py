"""Contrato para los lectores de eventos."""

from abc import ABC, abstractmethod

from src.utils.validacion import ValidadorEventos


class BaseLogParser(ABC):
    def __init__(self, validador=None):
        self._validador = ValidadorEventos() if validador is None else validador

    @abstractmethod
    def parse(self, ruta):
        """Devuelve (eventos válidos normalizados, cantidad de inválidos)."""
