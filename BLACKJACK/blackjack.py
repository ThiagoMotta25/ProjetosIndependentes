from os import system
import random

naipes = ['♠', '♥', '♦', '♣']
valores = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

baralho=[]
for naipe in naipes: # Une os naipes e os valores para criar o baralho de cartas
    for valor in valores:
       baralho += [f"{valor}{naipe}"]
baralho*=4       # Multiplica por 4 para ter mais combinações de cartas e menos chances de acabarem as cartas durante um jogo com várias rodadas

cartas_jogador= []
cartas_dealer=[]

valores_cartas = { # Dicionário que associa valores interiros aos valores das cartas
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


def buscar_carta():# Escolhe uma carta aleatoriamente do baralho
    carta = random.choice(baralho) 
    return carta


def extrair_valor(carta):
    valor=carta[:-1] # Remove o último caractere (naipe)
    pontos = valores_cartas[valor] # Busca o valor correspondente ao primeiro caractere (número/figura)

    return pontos


def distribuir_cartas():# Distribuição das cartas no início do jogo
    carta = buscar_carta()
    cartas_dealer.append(carta)
    baralho.remove(carta)

    while len(cartas_jogador)<2:
        nova_carta = buscar_carta()
        cartas_jogador.append(nova_carta)
        baralho.remove(nova_carta)
    

def pontuacao(mao): # Calcula a pontuação das cartas que o jogador possui
    pontos=0
    ases=0
    for cartas in mao:
        valor=extrair_valor(cartas)
        if valor==11:
            ases +=1
        pontos+=valor
    if pontos > 21 and ases > 1:
        pontos -= 10
        ases = 0
    
    return pontos

#-----------------------------------Funções das possíveis ações------------------------------------#


def pedir_carta(): # Adiciona mais uma carta a mão do jogador (HIT)
    if pontuacao(cartas_jogador) < 21:    
        carta = buscar_carta()
        cartas_jogador.append(carta)
        baralho.remove(carta)
        if pontuacao(cartas_jogador) > 21:
            manter()


def manter(): # Encerra turno do jogador e inicia ação de compra do dealer (STAND)
    while pontuacao(cartas_dealer) < 17:
        carta = buscar_carta()
        cartas_dealer.append(carta)
        baralho.remove(carta)

# Mãos partidas em caso de SPLIT
mao1=[]
mao2=[]
def partir(saldo,aposta): # Divide a mão do jogador em duas caso as cartas iniciais sejam iguais (SPLIT)

    
        if len(cartas_jogador) == 2 and extrair_valor(cartas_jogador[0]) == extrair_valor(cartas_jogador[1]): # Verifica se as duas cartas iniciais são iguais
            if saldo >= aposta*2:
                
                mao1.append(cartas_jogador[0])
                mao2.append(cartas_jogador[1])

                carta1 = buscar_carta()
                baralho.remove(carta1)
                carta2 = buscar_carta()
                baralho.remove(carta2)

                mao1.append(carta1)
                mao2.append(carta2)

                print(mao1 ,"\t",mao2)
                
            else:
                print("Saldo insuficiente para partir a mão.")
                print("\n")
                return 0
        else:
            print("Não é possível partir. As cartas precisam ter o mesmo valor.")
            print("\n")
            return 0
            


#-----------------------------------Funções sobre decisão do jogo------------------------------------#


# Decisao de vencedor
def resultado():
    pontos_jogador = pontuacao(cartas_jogador)
    pontos_dealer = pontuacao(cartas_dealer)
    
    if pontos_jogador == 21 and len(cartas_jogador) == 2:
        print("BLACKJACK!! Você Venceu!")
        return -1
    elif pontos_dealer == 21 and len(cartas_dealer)==2:
        print("Você Perdeu! Dealer teve BLACKJACK!!")
        return 0
    elif (pontos_dealer > pontos_jogador and pontos_dealer <= 21):
        print("Você Perdeu!")
        return 0
    elif pontos_jogador > 21:
        print("Estourou! Você perdeu.")
        return 0
    elif pontos_dealer == pontos_jogador:
        print("Vocês Empataram!")
        return 2
    elif (pontos_dealer < pontos_jogador and pontos_jogador <=21) or pontos_dealer > 21:
        print("Você Venceu!")
        return 1


# Decisao de vencedor após partir(SPLIT)
def resultado_partido(mao):
    pontos_jogador = pontuacao(mao)
    pontos_dealer = pontuacao(cartas_dealer)

    if pontos_jogador == 21 and len(mao) == 2:
        print("BLACKJACK!! Você Venceu!")
        return -1
    elif pontos_jogador > 21:
        print("Estourou! Você perdeu.")
        return 0
    elif pontos_dealer > 21 or pontos_jogador > pontos_dealer:
        print("Você Venceu!")
        return 1
    elif pontos_jogador == pontos_dealer:
        print("Empate!")
    else:
        print("Você Perdeu!")
        return 0
     

def jogo_partido(saldo,aposta): # Cria a situação de jogo com a mão do jogador partida em duas
    # Variaveis de apostas usadas em caso de dobrar aposta
    aposta_mao1 = aposta 
    aposta_mao2 = aposta

    print("\nJogando com a MÃO 1:")
    while pontuacao(mao1) < 21: # Jogo com a primeira mão
        menu(True)
        opcao = input("Escolha uma opção: ")
        if opcao == '1':
            carta = buscar_carta()
            mao1.append(carta)
            baralho.remove(carta)
        elif opcao == '3':
            break
        elif opcao == '4':
            aposta_mao1 = dobrar_aposta(saldo, aposta, mao1)
            break
        elif opcao == '0':
            return 0
        else:
            print("Opção inválida")
    
    system("cls")
    print("\nJogando com a MÃO 2:") 
    while pontuacao(mao2) < 21: # Jogo com a segunda mão
        menu(True)
        opcao = input("Escolha uma opção: ")
        if opcao == '1':
            carta = buscar_carta()
            mao2.append(carta)
            baralho.remove(carta)
            system("cls")
        elif opcao == '3':
            break
        elif opcao == '4':
            aposta_mao2 = dobrar_aposta(saldo, aposta, mao2)
            break
        elif opcao == '0':
            return 0
        else:
            print("Opção inválida")
    manter()
    return aposta_mao1, aposta_mao2 # Retorna as duas apostas para atualizar o saldo no fim da rodada
            

#-----------------------------------Funções sobre apostas--------------------------------------------#

def apostar(saldo): # Realiza a aposta utilizada na rodada
    while True:
        try:
            aposta=int(input(f"Saldo atual: {saldo}€. Quanto deseja apostar? "))

            if 0 < aposta < saldo:
                return aposta
            elif aposta == saldo:
                print("\n\t ALL IN !!!")
                return aposta
            else:
                print("Aposta inválida.")

        except:
            print("Aposta tem que ser um número inteiro\n")

def dobrar_aposta(saldo, aposta, mao): # Dobra o valor da posta em caso de possuir duas cartas e saldo suficiente (DOUBLE DOWN)
    # Mao esta declarado como parâmetro para que possa ser usada em jogo normal ou partido
    if len(mao) == 2:
        if saldo >= aposta*2: # Verifica se há saldo o suficiente para dobrar aposta
            aposta = aposta*2

            carta = buscar_carta()
            mao.append(carta)
            baralho.remove(carta)

            manter() # Encerra turno imediatamente após ganhar nova carta
            return aposta
        else:
            print("Saldo insuficiente para dobrar aposta.")
            return 0
    else:
        print("Não é possível dobrar com mais de uma carta")
        return 0

##########################################################################################################
##########################################################################################################


def menu(partido): # Menu de jogo (Normal e Mão Partida)
    if partido == False:   
        print("==========================================================================================")
        print(f"\t\t\tDealer: {cartas_dealer}  {pontuacao(cartas_dealer)} pontos\n")
        print(f"\t\tSua mão: {cartas_jogador}  {pontuacao(cartas_jogador)} pontos")
        print("==========================================================================================")
        print("\t 1. Pedir \t 2.Partir\t 3.Manter \t 4.Dobrar Aposta\t 0.Desistir\n")
    else:
        print("==========================================================================================")
        print(f"\t\t\tDealer: {cartas_dealer}  {pontuacao(cartas_dealer)} pontos\n")
        print(f"\t\tSuas mão: {mao1}  {pontuacao(mao1)} pontos \t{mao2} {pontuacao(mao2)} pontos")
        print("==========================================================================================")
        print("\t 1. Pedir \t 3.Manter \t 4.Dobrar Aposta \t 0.Desistir\n")


def main():
    system("cls") # Limpa o terminal
    
    saldo = 10000 # Saldo inicial
    replay = 's'

    input("\t\tAPERTE ENTER PARA JOGAR\n")
    while replay == 's': 
        aposta = apostar(saldo)
        # Para gerenciar apostas num jogo partido
        aposta_mao1 = aposta
        aposta_mao2 = aposta

        print("\n")

        distribuir_cartas()
        jogando = True # Variavel que mantém jogo ativo
        partido = False # Variavél que define qual dos dois tipos de menu a serão apresentados
            
        while jogando != False:
            
            if pontuacao(cartas_jogador)==21: # Condição para garantir BLACKJACK imediato
                break
            menu(partido)
            jogada=input("Escolha uma opção: ")

            if jogada == '1':
                system("cls")
                pedir_carta()
                print("\n")
                if pontuacao(cartas_jogador)>21: # Condição para causar o fim do jogo de imediato
                    jogando=False
            elif jogada == '2':
                system("cls")
                if partir(saldo,aposta) !=0: # Condição para garantir que jogo não corra caso opção seja escolhida com mais de 2 cartas ou cartas diferentes na mão do jogador
                    partido=True
                    aposta_mao1, aposta_mao2 = jogo_partido(saldo,aposta) # Busca o valor das apostas retornado pela função
                    print("\n")
                    jogando = False
            elif jogada == '3':
                system("cls")
                manter()
                print("\n")
                jogando = False
            elif jogada == '4':
                system("cls")
                aposta = dobrar_aposta(saldo, aposta, cartas_jogador)
                if aposta !=0: # Condição para garantir que jogo não corra caso opção seja escolhida com mais de 2 cartas na mão do jogador
                    print("\n")
                    jogando = False
            elif jogada =='0':
                print("Você desistiu do jogo")
                jogando = False
                return 0
            else:
                print("Opção não existe")
        
        if partido == False: # Mostra a mesa do jogo antes de ser anunciado o resultado da partida
            print("==========================================================================================")
            print(f"\t\t\tDealer: {cartas_dealer}  {pontuacao(cartas_dealer)} pontos\n")
            print(f"\t\tSua mão: {cartas_jogador}  {pontuacao(cartas_jogador)} pontos")
            print("==========================================================================================")
            resultado_final = resultado()
            if resultado_final == 1:
                saldo += aposta # Venceu na rodada
                print("Saldo atual: ",saldo,"€")
            elif resultado_final == 0:
                saldo -= aposta # Perdeu na rodada
                print("Saldo atual: ",saldo,"€")
            elif resultado_final == -1:
                saldo += int(aposta * 1.5) # Venceu com BLACKJACK
                print("Saldo atual: ",saldo,"€")
            else: # Empatou na rodada
                print("Saldo atual: ",saldo,"€")
                
            
        if partido == True: # Mostra a mesa do jogo, após a mão do jogador ser partida, antes de ser anunciado o resultado da partida
            print("==========================================================================================")
            print(f"\t\t\tDealer: {cartas_dealer}  {pontuacao(cartas_dealer)} pontos\n")
            print(f"\t\tSuas mão: {mao1}  {pontuacao(mao1)} pontos \t{mao2} {pontuacao(mao2)} pontos")
            print("==========================================================================================")
            resultado_final_1 = resultado_partido(mao1)
            resultado_final_2 = resultado_partido(mao2)
            if resultado_final_1 == 1:
                saldo += aposta_mao1 # Venceu na rodada
                print("Saldo atual com resultado da mão1: ",saldo,"€")
            elif resultado_final_1 ==0:
                saldo -= aposta_mao1 # Perdeu na rodada
                print("Saldo atual com resultado da mão1: ",saldo,"€")
            elif resultado_final_1 == -1:
                saldo += int(aposta_mao1 * 1.5) # Venceu com BLACKJACK
                print("Saldo atual com resultado da mão1: ",saldo,"€")
            else: # Empatou na rodada
                print("Saldo atual com resultado da mão1: ",saldo,"€")
                

            if resultado_final_2 == 1:
                saldo += aposta_mao2 # Venceu na rodada
                print("Saldo atual com resultado da mão2: ",saldo,"€")
            elif resultado_final_2 ==0:
                saldo -= aposta_mao2 # Perdeu na rodada
                print("Saldo atual com resultado da mão2: ",saldo,"€")
            elif resultado_final_2 == -1:
                saldo += int(aposta_mao2 * 1.5) # Venceu com BLACKJACK
                print("Saldo atual com resultado da mão2: ",saldo,"€")
            else: # Empatou na rodada
                print("Saldo atual com resultado da mão2: ",saldo,"€")
                
       
        print("\n")
        if saldo == 0:
            print("Você Faliu.\n")
            replay =='n'
            return 0
        else:
            replay = input("Quer continuar jogando?(S/N) ")

        cartas_dealer.clear() # remove todas as cartas da mão do dealer
        cartas_jogador.clear() # remove todas as cartas da mão do jogador
        mao1.clear() # remove todas as cartas da primeira mão partida do jogador
        mao2.clear() # remove todas as cartas da segunda mão partida do jogador

        

    



if __name__=="__main__":
    print("\n")   
    main()
    print("\n") 