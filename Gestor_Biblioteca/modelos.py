# modelos.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Livro:
    id: Optional[int]
    titulo: str
    autores: List[str]
    ano: Optional[int] = None
    isbn: Optional[str] = None
    paginas: Optional[int] = None
    editora: Optional[str] = None


@dataclass
class Utilizador:
    id: Optional[int]
    nome: str
    email: Optional[str] = None


@dataclass
class Emprestimo:
    id: Optional[int]
    livro_id: int
    utilizador_id: int
    data_emprestimo: str
    data_prevista: str
    data_devolucao: Optional[str] = None
