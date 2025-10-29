from django.shortcuts import redirect, render, HttpResponse
from django.contrib import messages
import mysql.connector


cnx = mysql.connector.connect(user='jd0425',
            password='123.Abc',host='62.28.39.135',
            port='3306',database='jd0425_18_projetofinal')
mycursor = cnx.cursor()

# Remove duplicatas com base em Nome, Artista, Album e Ano_lancamento, mantendo a de menor id_musica    
#    mycursor.execute("""DELETE m1 FROM musica m1
#        INNER JOIN musica m2 
#            ON m1.Nome = m2.Nome 
#            AND m1.Artista = m2.Artista 
#            AND m1.Album = m2.Album
#            AND m1.Ano_lancamento = m2.Ano_lancamento
#            AND m1.id_musica > m2.id_musica;""")
#    cnx.commit()

def home(request):
    return render(request, "home.html")

def sobre(request):
    return render(request,'sobre.html')

########################################################################################################
########################################## AUTENTICAÇÃO ################################################
########################################################################################################

def login(request):
    request.session.flush()  # Limpa todos os dados da sessão ao acessar a página de login
    if request.method == 'POST':
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        
        mycursor.execute("SELECT * FROM usuario WHERE email = %s AND senha= %s", (email, senha))
        existe = mycursor.fetchone()
        if existe is not None:
            request.session['usuario_id'] = existe[0]  # salva o id do usuário
            return redirect('home')
        else:
            messages.error(request, 'Email e/ou senha inválidos.')
            return render(request, "login.html")
        
    return render(request, "login.html")

def logout(request):
    request.session.flush()  # Limpa todos os dados da sessão
    return redirect('login')

def sign_up(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Validação dos dados
        if len(senha) < 7:
            messages.error(request, 'Senha tem que ter pelo menos 7 caracteres.')
            return render(request, "sign_up.html")
        
        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, "sign_up.html")

        # Verifica se o nome de usuário já existe
        mycursor.execute("SELECT * FROM usuario WHERE nome = %s", (nome,))
        usuario_existente = mycursor.fetchone()
        if usuario_existente is not None:
            messages.error(request, 'Nome de usuario já existe.')
            return render(request, "sign_up.html")

        # Insere o novo usuário no banco de dados
        mycursor.execute("INSERT INTO usuario (Nome, Email, Senha) VALUES (%s, %s, %s)", (nome, email, senha))
        cnx.commit()
        
        messages.success(request, 'Conta criada com sucesso. Já pode fazer o login.')
        return redirect('login')

    return render(request, "sign_up.html")

########################################################################################################
class Usuario:
    def __init__(self, id_usuario, nome, email, senha, foto_perfil):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.senha = senha
        self.foto_perfil = foto_perfil

def perfil(request):
    mycursor.execute("SELECT * FROM usuario WHERE Id_usuario = %s;", (request.session.get('usuario_id'),))
    usuario = mycursor.fetchone()
    if usuario:
        usuario = Usuario(*usuario) # Desempacota a tupla diretamente na criação do objeto
    
    #Conta quantas playlists o usuário tem
    mycursor.execute("SELECT COUNT(*) FROM playlist WHERE IdUsuario = %s;", (request.session.get('usuario_id'),))
    num_playlists = mycursor.fetchone()

    if request.method == 'POST':
        if 'foto' in request.FILES:
            foto = request.FILES['foto'] # Pega o arquivo enviado

            if not foto.content_type.startswith('image/'):
                messages.error(request, 'O arquivo enviado não é uma imagem válida.')
                return redirect('perfil')
            
            if foto.size > 5 * 1024 * 1024:
                messages.error(request, 'A imagem deve ter no máximo 5MB.')
                return redirect('perfil')
            
            foto = foto.read()  # Lê o conteúdo binário da imagem
            mycursor.execute("UPDATE usuario SET foto_perfil = %s WHERE Id_usuario = %s", (foto, request.session.get('usuario_id')))
            cnx.commit()
            return redirect('perfil')
        
        else:
            novo_nome = request.POST.get('nome')
            novo_email = request.POST.get('email')
            nova_senha = request.POST.get('senha')

            if not novo_nome or not novo_email or not nova_senha: # Verifica se algum campo está vazio
                messages.error(request, 'Todos os campos são obrigatórios.')
                return redirect('perfil')

            if len(nova_senha) < 7:
                messages.error(request, 'Senha tem que ter pelo menos 7 caracteres.')
                return redirect('perfil')

            # Verifica se o novo nome de usuário já existe (excluindo o usuário atual)
            mycursor.execute("SELECT * FROM usuario WHERE Nome = %s AND Id_usuario != %s", (novo_nome, request.session.get('usuario_id')))
            usuario_existente = mycursor.fetchone()
            if usuario_existente is not None:
                messages.error(request, 'Nome de usuario já existe.')
                return redirect('perfil')

            # Atualiza os dados do usuário no banco de dados
            mycursor.execute("UPDATE usuario SET Nome = %s, Email = %s, Senha = %s WHERE Id_usuario = %s", (novo_nome, novo_email, nova_senha, request.session.get('usuario_id')))
            cnx.commit()


        return redirect('perfil')
    
    ############################## Deletar conta ########################################
    # Usando método GET para evitar problemas com CSRF e facilitar a confirmação via link
    if request.method == 'GET' and 'delete' in request.GET:
        mycursor.execute("DELETE FROM usuario WHERE Id_usuario = %s", (request.session.get('usuario_id'),))
        cnx.commit()
        request.session.flush()  # Limpa todos os dados da sessão
        messages.success(request, 'Conta eliminada com sucesso.')
        return redirect('login')
    

    return render(request, "perfil.html", {'usuario': usuario, 'num_playlists': num_playlists})

def foto_perfil(request, usuario_id):
    mycursor.execute("SELECT foto_perfil FROM usuario WHERE Id_usuario = %s", (usuario_id,))
    resultado = mycursor.fetchone()
    
    if resultado and resultado[0]:# Se houver foto no banco de dados
        return HttpResponse(resultado[0], content_type="image/png")
    else:
        # Retorna a imagem padrão se não houver foto
        with open('static/empty_profile.png', 'rb') as foto:
            return HttpResponse(foto.read(), content_type="image/png")
    
########################################################################################################
############################################### MÚSICAS ################################################
########################################################################################################
class Musica:
    def __init__(self, id, nome, artista, album, ano):
        self.id = id
        self.nome = nome
        self.artista = artista
        self.album = album
        self.ano = ano

def musicas(request):
    pesquisa = request.POST.get('pesquisa', '') if request.method == 'POST' else ''

    if pesquisa:
        # Filtra por nome ou artista usando LIKE
        mycursor.execute("SELECT * FROM musica WHERE nome LIKE %s OR artista LIKE %s ORDER BY nome;", ('%' + pesquisa + '%', '%' + pesquisa+ '%'))
    else:
        # Se não houver pesquisa, traz todas as músicas
        mycursor.execute("SELECT * FROM musica;")

    resultado = mycursor.fetchall()

    lista_musicas = []
    for (id, nome, artista, album, ano) in resultado:
        lista_musicas.append(Musica(id, nome, artista, album, ano))

    ##################### Adicionar música a uma playlist ###############################

    if request.method == 'POST':
        ids_musica = request.POST.getlist('id_musica')
        id_playlist = request.POST.get('id_playlist')

        if id_playlist and ids_musica:
            for id_musica in ids_musica:
                # Verifica se a música já está na playlist
                mycursor.execute("SELECT * FROM playlist_musica WHERE Id_playlist = %s AND Id_musica = %s;", (id_playlist, id_musica))
                music_existente = mycursor.fetchone()
                
                if music_existente is None:
                    mycursor.execute("INSERT INTO playlist_musica (Id_playlist, Id_musica) VALUES (%s, %s);", (id_playlist, id_musica))
            
            cnx.commit()
            return redirect('musicas')

        else:
            messages.error(request, 'Música já está na playlist.')
            return redirect('musicas')
    else:
        mycursor.execute("SELECT * FROM playlist WHERE IdUsuario LIKE %s;", (request.session.get('usuario_id'),))
        playlists_usuario = mycursor.fetchall()

        lista_playlists = []
        for (id, nome,id_usuario) in playlists_usuario:
            lista_playlists.append(Playlist(id, nome, id_usuario))
    

    return render(request, 'musicas.html', {'musicas': lista_musicas, 'pesquisa': pesquisa, 'playlists': lista_playlists})
    

########################################################################################################
############################################### PLAYLISTS ##############################################
########################################################################################################

class Playlist:
    def __init__(self, id, nome,id_usuario):
        self.id = id
        self.nome = nome
        self.id_usuario = id_usuario
    
def playlists(request):
    mycursor.execute("SELECT * FROM playlist WHERE IdUsuario LIKE %s;", (request.session.get('usuario_id'),))
    resultado = mycursor.fetchall()

    lista_playlists = []
    for (id, nome,id_usuario) in resultado:
        lista_playlists.append(Playlist(id, nome, id_usuario))

    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            mycursor.execute("INSERT INTO playlist (Nome, IdUsuario) VALUES (%s, %s);", (nome, request.session.get('usuario_id')))
            cnx.commit()
            return redirect('playlists')
    
    mycursor.execute("SELECT Id_playlist, COUNT(Id_musica) FROM playlist_musica GROUP BY Id_playlist;")
    num_musicas = dict(mycursor.fetchall())

    return render(request, "playlists.html", {'playlists': lista_playlists, 'num_musicas': num_musicas})

def playlist_detalhe(request, id):
    # Pega dados da playlist
    mycursor.execute("SELECT * FROM playlist WHERE Id_playlist = %s;", (id,))
    playlist = mycursor.fetchone()

    # Busca músicas associadas a essa playlist (via tabela associativa)
    mycursor.execute("""
        SELECT m.Id_musica, m.nome, m.artista, m.album, m.ano_lancamento
        FROM playlist_musica pm
        JOIN musica m ON pm.Id_musica = m.Id_musica
        WHERE pm.Id_playlist = %s;
    """, (id,))
    musicas = mycursor.fetchall()

    lista_musicas = [Musica(*musica) for musica in musicas]
    
    ##################### Remover música da playlist ###############################
    if request.method == 'POST':
        id_musica = request.POST.get('remove_musica')
        mycursor.execute("DELETE FROM playlist_musica WHERE Id_playlist = %s AND Id_musica = %s;", (id, id_musica))
        cnx.commit()
        return redirect('playlist_detalhe', id=id)
    
    ##################### Deletar playlist ###############################
    # Usa método GET para evitar problemas com CSRF e facilitar a confirmação via link
    if request.method == 'GET' and 'delete' in request.GET:
        mycursor.execute("DELETE FROM playlist_musica WHERE Id_playlist = %s ;", (id,))
        mycursor.execute("DELETE FROM playlist WHERE Id_playlist = %s ;", (id,))
        cnx.commit()
        return redirect('playlists')
    return render(request, "playlist_detalhe.html", {"playlist": playlist,"musicas": lista_musicas})

