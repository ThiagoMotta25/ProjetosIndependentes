import sqlite3
import json
import csv
import os
from dataclasses import asdict
from datetime import date, datetime
from modelos import Livro, Utilizador, Emprestimo
from menus import *


class GestorBD:
    def __init__(self, caminho_bd: str = "biblioteca.db"):
        self.caminho_bd = caminho_bd
        self.inicializar_bd()

    def conexao(self):
        return sqlite3.connect(self.caminho_bd)

    def inicializar_bd(self):
        """Cria as tabelas se não existirem"""
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            
            # Tabela livros
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS livros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    titulo TEXT NOT NULL,
                    autores TEXT,
                    ano INTEGER,
                    isbn TEXT,
                    paginas INTEGER,
                    editora TEXT
                )
            """)
            
            # Tabela utilizadores
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS utilizadores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE
                )
            """)
            
            # Tabela emprestimos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emprestimos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    livro_id INTEGER NOT NULL,
                    utilizador_id INTEGER NOT NULL,
                    data_emprestimo TEXT NOT NULL,
                    data_prevista TEXT NOT NULL,
                    data_devolucao TEXT,
                    FOREIGN KEY (livro_id) REFERENCES livros (id),
                    FOREIGN KEY (utilizador_id) REFERENCES utilizadores (id)
                )
            """)
            
            conexao.commit()

    # ---------------- LIVROS ----------------
    def inserir_livro(self, livro: Livro) -> int:
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO livros (titulo, autores, ano, isbn, paginas, editora)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                livro.titulo,
                json.dumps(livro.autores) if livro.autores else None,
                livro.ano,
                livro.isbn,
                livro.paginas,
                livro.editora,
            ))
            conexao.commit()
            return cursor.lastrowid

    def pesquisar_livros(self, termo: str):
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT * FROM livros 
                WHERE titulo LIKE ? OR autores LIKE ? OR isbn LIKE ?
            """, (f"%{termo}%", f"%{termo}%", f"%{termo}%"))
            resultados = cursor.fetchall()
            livros = []
            for linha in resultados:
                livros.append(Livro(
                    id=linha[0],
                    titulo=linha[1],
                    autores=json.loads(linha[2]) if linha[2] else [],
                    ano=linha[3],
                    isbn=linha[4],
                    paginas=linha[5],
                    editora=linha[6],    
                ))
            return livros

    def listar_todos_livros(self):
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM livros")
            resultados = cursor.fetchall()
            livros = []
            for linha in resultados:
                livros.append(Livro(
                    id=linha[0],
                    titulo=linha[1],
                    autores=json.loads(linha[2]) if linha[2] else [],
                    ano=linha[3],
                    isbn=linha[4],
                    paginas=linha[5],
                    editora=linha[6],    
                ))
            return livros

    def livro_por_id(self, livro_id: int) -> Livro | None:
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, titulo, autores, ano, isbn, paginas, editora 
                FROM livros WHERE id = ?
            """, (livro_id,))
            linha = cursor.fetchone()
            if not linha:
                return None
            return Livro(
                id=linha[0],
                titulo=linha[1],
                autores=json.loads(linha[2]) if linha[2] else [],
                ano=linha[3],
                isbn=linha[4],
                paginas=linha[5],
                editora=linha[6],
            )

    # ---------------- UTILIZADORES ----------------
    def inserir_utilizador(self, utilizador: Utilizador) -> int:
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO utilizadores (nome, email)
                VALUES (?, ?)
            """, (utilizador.nome, utilizador.email))
            conexao.commit()
            return cursor.lastrowid

    def listar_todos_utilizadores(self):
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT id, nome, email FROM utilizadores")
            resultados = cursor.fetchall()
            utilizadores = []
            for linha in resultados:
                utilizadores.append(Utilizador(
                    id=linha[0],
                    nome=linha[1],
                    email=linha[2]
                ))
            return utilizadores

    def utilizador_por_id(self, utilizador_id: int) -> Utilizador | None:
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id, nome, email FROM utilizadores WHERE id = ?
            """, (utilizador_id,))
            linha = cursor.fetchone()
            if not linha:
                return None
            return Utilizador(id=linha[0], nome=linha[1], email=linha[2])

    def editar_utilizador(self, utilizador_id: int, nome: str | None = None, email: str | None = None) -> bool:
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            campos, valores = [], []
            if nome:
                campos.append("nome = ?")
                valores.append(nome)
            if email:
                campos.append("email = ?")
                valores.append(email)

            if not campos:
                return False

            valores.append(utilizador_id)
            sql = f"UPDATE utilizadores SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(sql, valores)
            conexao.commit()
            return cursor.rowcount > 0

    def remover_utilizador(self, utilizador_id: int) -> bool:
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM utilizadores WHERE id = ?", (utilizador_id,))
            conexao.commit()
            return cursor.rowcount > 0

    # ---------------- EMPRÉSTIMOS ----------------
    def criar_emprestimo(self, livro_id: int, utilizador_id: int, data_prevista: str) -> int:
        data_hoje = date.today().isoformat()
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO emprestimos (livro_id, utilizador_id, data_emprestimo, data_prevista)
                VALUES (?, ?, ?, ?)
            """, (livro_id, utilizador_id, data_hoje, data_prevista))
            conexao.commit()
            return cursor.lastrowid

    def livro_emprestado(self, livro_id: int) -> bool:
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id FROM emprestimos 
                WHERE livro_id = ? AND data_devolucao IS NULL
            """, (livro_id,))
            return cursor.fetchone() is not None

    def devolver_livro(self, emprestimo_id: int):
        data_devolucao = date.today().isoformat()
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE emprestimos SET data_devolucao = ? WHERE id = ?
            """, (data_devolucao, emprestimo_id))
            conexao.commit()

    def listar_emprestimos_ativos(self):
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT e.id, l.titulo, u.nome, e.data_emprestimo, e.data_prevista
                FROM emprestimos e
                JOIN livros l ON e.livro_id = l.id
                JOIN utilizadores u ON e.utilizador_id = u.id
                WHERE e.data_devolucao IS NULL
                ORDER BY e.data_emprestimo
            """)
            return cursor.fetchall()

    def emprestimo_por_livro(self, livro_id: int):
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT id FROM emprestimos 
                WHERE livro_id = ? AND data_devolucao IS NULL
            """, (livro_id,))
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None

    def historico_emprestimos_utilizador(self, utilizador_id: int):
        """Histórico de todos os empréstimos de um utilizador"""
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT e.id, l.titulo, e.data_emprestimo, e.data_prevista, e.data_devolucao,
                       CASE WHEN e.data_devolucao IS NULL THEN 'Ativo' ELSE 'Devolvido' END as status
                FROM emprestimos e
                JOIN livros l ON e.livro_id = l.id
                WHERE e.utilizador_id = ?
                ORDER BY e.data_emprestimo DESC
            """, (utilizador_id,))
            return cursor.fetchall()

    def historico_emprestimos_livro(self, livro_id: int):
        """Histórico de todos os empréstimos de um livro"""
        with self.conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT e.id, u.nome, e.data_emprestimo, e.data_prevista, e.data_devolucao,
                        CASE WHEN e.data_devolucao IS NULL THEN 'Ativo' ELSE 'Devolvido' END as status
                FROM emprestimos e
                JOIN utilizadores u ON e.utilizador_id = u.id
                WHERE e.livro_id = ?
                ORDER BY e.data_emprestimo DESC
            """, (livro_id,))
            return cursor.fetchall()


# ---------------- FUNÇÕES DO MENU ----------------

def limpar_tela():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

def pausar():
    input("\nPressione Enter para continuar...")


def adicionar_livro(gestor):
    print("\n--- ADICIONAR LIVRO ---")
    titulo = input("Título: ").strip()
    if not titulo:
        print("Título é obrigatório!")
        return
    
    autores_input = input("Autores (separados por vírgula): ").strip()
    autores = [autor.strip() for autor in autores_input.split(",")] if autores_input else []
    
    try:
        ano = int(input("Ano de publicação: ").strip())
    except ValueError:
        ano = None
    
    isbn = input("ISBN: ").strip() or None
    
    try:
        paginas = int(input("Número de páginas: ").strip())
    except ValueError:
        paginas = None
    
    editora = input("Editora: ").strip() or None
    
    livro = Livro(None, titulo, autores, ano, isbn, paginas, editora)
    livro_id = gestor.inserir_livro(livro)
    print(f"Livro adicionado com sucesso! ID: {livro_id}")
    gravarLivroCSV(livro, "Livros.csv")

def pesquisar_livros(gestor):
    print("\n--- PESQUISAR LIVROS ---")
    termo = input("Digite o termo de pesquisa (título, autor ou ISBN): ").strip()
    if not termo:
        print("Termo de pesquisa não pode estar vazio!")
        return
    
    livros = gestor.pesquisar_livros(termo)
    if not livros:
        print("Nenhum livro encontrado.")
        return
    
    print(f"\nEncontrados {len(livros)} livro(s):")
    for livro in livros:
        status = "Emprestado" if gestor.livro_emprestado(livro.id) else "Disponível"
        print(f"ID: {livro.id} | {livro.titulo} | Autores: {', '.join(livro.autores)} | Status: {status}")

def listar_livros(gestor):
    print("\n--- TODOS OS LIVROS ---")
    livros = gestor.listar_todos_livros()
    if not livros:
        print("Nenhum livro cadastrado.")
        return
    
    for livro in livros:
        status = "Emprestado" if gestor.livro_emprestado(livro.id) else "Disponível"
        print(f"ID: {livro.id} | {livro.titulo} | Autores: {', '.join(livro.autores)} | Status: {status}")

def ver_detalhes_livro(gestor):
    print("\n--- DETALHES DO LIVRO ---")
    try:
        livro_id = int(input("ID do livro: "))
        livro = gestor.livro_por_id(livro_id)
        if not livro:
            print("Livro não encontrado!")
            return
        
        print(f"\nTítulo: {livro.titulo}")
        print(f"Autores: {', '.join(livro.autores)}")
        print(f"Ano: {livro.ano}")
        print(f"ISBN: {livro.isbn}")
        print(f"Páginas: {livro.paginas}")
        print(f"Editora: {livro.editora}")
        print(f"Status: {'Emprestado' if gestor.livro_emprestado(livro.id) else 'Disponível'}")
        
    except ValueError:
        print("ID inválido!")

########################################################################################
#---------------- FUNÇÕES DE UTILIZADORES ----------------##############################
########################################################################################

def adicionar_utilizador(gestor):
    print("\n--- ADICIONAR UTILIZADOR ---")
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome é obrigatório!")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("Email é obrigatório!")
        return
    
    utilizador = Utilizador(None, nome, email)
    try:
        utilizador_id = gestor.inserir_utilizador(utilizador)
        print(f"Utilizador adicionado com sucesso! ID: {utilizador_id}")
        gravarUtilizadorCSV(utilizador, "Utilizadores.csv")
    except sqlite3.IntegrityError:
        print("Erro: Email já existe na base de dados!")


def listar_utilizadores(gestor):
    print("\n--- TODOS OS UTILIZADORES ---")
    utilizadores = gestor.listar_todos_utilizadores()
    if not utilizadores:
        print("Nenhum utilizador cadastrado.")
        return
    
    for utilizador in utilizadores:
        print(f"ID: {utilizador.id} | Nome: {utilizador.nome} | Email: {utilizador.email}")

def editar_utilizador(gestor):
    print("\n--- EDITAR UTILIZADOR ---")
    try:
        utilizador_id = int(input("ID do utilizador: "))
        utilizador = gestor.utilizador_por_id(utilizador_id)
        if not utilizador:
            print("Utilizador não encontrado!")
            return
        
        print(f"Dados atuais - Nome: {utilizador.nome}, Email: {utilizador.email}")
        
        nome = input("Novo nome (deixe vazio para manter atual): ").strip()
        email = input("Novo email (deixe vazio para manter atual): ").strip()
        
        if gestor.editar_utilizador(utilizador_id, nome if nome else None, email if email else None):
            print("Utilizador editado com sucesso!")
        else:
            print("Nenhuma alteração foi feita.")
            
    except ValueError:
        print("ID inválido!")
    except sqlite3.IntegrityError:
        print("Erro: Email já existe na base de dados!")

def remover_utilizador(gestor):
    print("\n--- REMOVER UTILIZADOR ---")
    try:
        utilizador_id = int(input("ID do utilizador: "))
        utilizador = gestor.utilizador_por_id(utilizador_id)
        if not utilizador:
            print("Utilizador não encontrado!")
            return
        
        confirmacao = input(f"Tem certeza que deseja remover '{utilizador.nome}'? (s/N): ").strip().lower()
        if confirmacao == 's':
            if gestor.remover_utilizador(utilizador_id):
                print("Utilizador removido com sucesso!")
            else:
                print("Erro ao remover utilizador.")
        else:
            print("Operação cancelada.")
            
    except ValueError:
        print("ID inválido!")

########################################################################################
#---------------- FUNÇÕES DE EMPRÉSTIMOS ----------------###############################
########################################################################################

def fazer_emprestimo(gestor):
    print("\n--- FAZER EMPRÉSTIMO ---")
    try:
        livro_id = int(input("ID do livro: "))
        livro = gestor.livro_por_id(livro_id)
        if not livro:
            print("Livro não encontrado!")
            return
        
        if gestor.livro_emprestado(livro_id):
            print("Este livro já está emprestado!")
            return
        
        utilizador_id = int(input("ID do utilizador: "))
        utilizador = gestor.utilizador_por_id(utilizador_id)
        if not utilizador:
            print("Utilizador não encontrado!")
            return
        
        data_prevista = input("Data prevista de devolução (AAAA-MM-DD): ").strip()
        try:
            datetime.strptime(data_prevista, '%Y-%m-%d')
        except ValueError:
            print("Formato de data inválido!")
            return
        
        emprestimo_id = gestor.criar_emprestimo(livro_id, utilizador_id, data_prevista)
        print(f"Empréstimo criado com sucesso! ID: {emprestimo_id}")
        print(f"Livro '{livro.titulo}' emprestado para '{utilizador.nome}'")
        
    except ValueError:
        print("ID inválido!")

def devolver_livro(gestor):
    print("\n--- DEVOLVER LIVRO ---")
    try:
        livro_id = int(input("ID do livro a devolver: "))
        livro = gestor.livro_por_id(livro_id)
        if not livro:
            print("Livro não encontrado!")
            return
        
        emprestimo_id = gestor.emprestimo_por_livro(livro_id)
        if not emprestimo_id:
            print("Este livro não está emprestado!")
            return
        
        gestor.devolver_livro(emprestimo_id)
        print(f"Livro '{livro.titulo}' devolvido com sucesso!")
        
    except ValueError:
        print("ID inválido!")

def listar_emprestimos_ativos(gestor):
    print("\n--- EMPRÉSTIMOS ATIVOS ---")
    emprestimos = gestor.listar_emprestimos_ativos()
    if not emprestimos:
        print("Nenhum empréstimo ativo.")
        return
    
    print("ID | Livro | Utilizador | Data Empréstimo | Data Prevista")
    print("-" * 70)
    for emp in emprestimos:
        print(f"{emp[0]} | {emp[1]} | {emp[2]} | {emp[3]} | {emp[4]}")

##########################################################################################
#---------------- FUNÇÕES DE RELATÓRIOS/HISTÓRICOS ----------------#######################
##########################################################################################


def historico_utilizador(gestor):
    print("\n--- HISTÓRICO DE EMPRÉSTIMOS DO UTILIZADOR ---")
    try:
        utilizador_id = int(input("ID do utilizador: "))
        utilizador = gestor.utilizador_por_id(utilizador_id)
        if not utilizador:
            print("Utilizador não encontrado!")
            return
        
        emprestimos = gestor.historico_emprestimos_utilizador(utilizador_id)
        if not emprestimos:
            print(f"Nenhum empréstimo encontrado para {utilizador.nome}.")
            return
        
        print(f"\nHistórico de {utilizador.nome}:")
        print("ID | Utilizador | Data Empréstimo | Data Prevista | Status | Data Devolução")
        print("-" * 80)
        for emp in emprestimos:
            data_devolucao = emp[4] if emp[4] else "---"
            print(f"{emp[0]} | {emp[1]} | {emp[2]} | {emp[3]} | {emp[5]} | {data_devolucao}")
            
    except ValueError:
        print("ID inválido!")

def historico_livro(gestor):
    print("\n--- HISTÓRICO DE EMPRÉSTIMOS DO LIVRO ---")
    try:
        livro_id = int(input("ID do livro: "))
        livro = gestor.livro_por_id(livro_id)
        if not livro:
            print("Livro não encontrado!")
            return
        
        emprestimos = gestor.historico_emprestimos_livro(livro_id)
        if not emprestimos:
            print(f"Nenhum empréstimo encontrado para '{livro.titulo}'.")
            return
        
        print(f"\nHistórico de '{livro.titulo}':")
        print("ID | Utilizador | Data Empréstimo | Data Prevista | Status | Data Devolução")
        print("-" * 80)
        for emp in emprestimos:
            data_devolucao = emp[4] if emp[4] else "---"
            print(f"{emp[0]} | {emp[1]} | {emp[2]} | {emp[3]} | {emp[5]} | {data_devolucao}")
            
    except ValueError:
        print("ID inválido!")


def gravarLivroCSV(livro: Livro, caminho: str) -> None:

    novo_arquivo = not os.path.exists(caminho)
    # Cria/reescreve o CSV com cabeçalho e 1 livro.
    with open(caminho, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "titulo", "autores", "ano", "isbn", "paginas", "editora"],
            delimiter=";"
        )
        if novo_arquivo:
            writer.writeheader()
        # autores deve ser convertido para string (ex: separado por vírgula)
        livro_dict = asdict(livro)
        if isinstance(livro_dict.get("autores"), list):
            livro_dict["autores"] = ", ".join(livro_dict["autores"])
        writer.writerow(livro_dict)

def gravarUtilizadorCSV(utilizador: Utilizador, caminho: str) -> None:
    novo_arquivo = not os.path.exists(caminho)
    # Cria/reescreve o CSV com cabeçalho e 1 utilizador.
    with open(caminho, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "nome", "email"],
            delimiter=";"
        )
        if novo_arquivo:
            writer.writeheader()
        writer.writerow(asdict(utilizador))

    