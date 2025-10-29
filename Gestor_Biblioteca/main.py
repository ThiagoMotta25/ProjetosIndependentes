from gestor import *


def main():
    gestor = GestorBD()
    
    while True:
        limpar_tela()
        menu_principal()
        
        try:
            opcao = int(input("Escolha uma opção: "))
        except ValueError:
            print("Opção inválida!")
            pausar()
            continue
        
        if opcao == 0:
            print("Saindo do sistema...")
            break
        elif opcao == 1:
            while True:
                limpar_tela()
                menu_livros()
                try:
                    sub_opcao = int(input("Escolha uma opção: "))
                except ValueError:
                    print("Opção inválida!")
                    pausar()
                    continue
                
                if sub_opcao == 0:
                    break
                elif sub_opcao == 1:
                    adicionar_livro(gestor)
                elif sub_opcao == 2:
                    pesquisar_livros(gestor)
                elif sub_opcao == 3:
                    listar_livros(gestor)
                elif sub_opcao == 4:
                    ver_detalhes_livro(gestor)
                else:
                    print("Opção inválida!")
                
                pausar()
                
        elif opcao == 2:
            while True:
                limpar_tela()
                menu_utilizadores()
                try:
                    sub_opcao = int(input("Escolha uma opção: "))
                except ValueError:
                    print("Opção inválida!")
                    pausar()
                    continue
                
                if sub_opcao == 0:
                    break
                elif sub_opcao == 1:
                    adicionar_utilizador(gestor)
                elif sub_opcao == 2:
                    listar_utilizadores(gestor)
                elif sub_opcao == 3:
                    editar_utilizador(gestor)
                elif sub_opcao == 4:
                    remover_utilizador(gestor)
                else:
                    print("Opção inválida!")
                
                pausar()
                
        elif opcao == 3:
            while True:
                limpar_tela()
                menu_emprestimos()
                try:
                    sub_opcao = int(input("Escolha uma opção: "))
                except ValueError:
                    print("Opção inválida!")
                    pausar()
                    continue
                
                if sub_opcao == 0:
                    break
                elif sub_opcao == 1:
                    fazer_emprestimo(gestor)
                elif sub_opcao == 2:
                    devolver_livro(gestor)
                elif sub_opcao == 3:
                    listar_emprestimos_ativos(gestor)
                elif sub_opcao == 4:
                    historico_utilizador(gestor)
                elif sub_opcao == 5:
                    historico_livro(gestor)
                else:
                    print("Opção inválida!")
                
                pausar()
                
        elif opcao == 4:
            pass
        else:
            print("Opção inválida!")
            pausar()

if __name__ == "__main__":
    main()