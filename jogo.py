import os
import os.path
import cv2

# Atribuir as fotos de Pedra, Papel e Tesoura em variáveis
templatePapel = cv2.resize(cv2.imread("fotos/papel.png", 0), (0, 0), None, 0.400, 0.400)
templateTesoura = cv2.resize(cv2.imread("fotos/tesoura.png", 0), (0, 0), None, 0.400, 0.400)
templatePedra = cv2.resize(cv2.imread("fotos/pedra.png", 0), (0, 0), None, 0.400, 0.400)

# Inverter as imagens de Pedra, Papel e Tesoura para identificar as jogadas da direita
reverterTemplatePapel = cv2.flip(templatePapel, -1)
reverterTemplateTesoura = cv2.flip(templateTesoura, -1)
reverterTemplatePedra = cv2.flip(templatePedra, -1)

# Definção das variáveis que serão utilizadas no checkpoint
tesoura = "Tesoura"
pedra = "Pedra"
papel = "Papel"
movNaoIdentificado = "Jogada não identificada"

# Valor minimo de comparação do match das jogadas
acharPapel = 0.017
acharTesoura  = 0.031
acharPedra  = 0.0099

jogador1 = "Jogador 1"
jogador2 = "Jogador 2"

placar = [0, 0]
cor = [255, 75, 0]

# Definição das globais que vão ser utilizadas
ultimajogada1 = ""
ultimajogada2 = ""
ultimoJogadorVence = ""
ultimoPlacar = ""

# Função para mostrar em tela os textos
def mostrarNaTela(img, text, origem, cor):
    font = cv2.FONT_ITALIC
    cv2.putText(img, str(text), origem, font,0.7,cor,2,cv2.LINE_AA)

# Função para encontrar o movimento de cada jogador e descrever a jogada
def movimento(imgGray, imgRgb, templatePapel, templateTesoura, templatePedra):
    correspondePapel = cv2.matchTemplate(imgGray, templatePapel, cv2.TM_SQDIFF_NORMED)
    correspondeTesoura = cv2.matchTemplate(imgGray, templateTesoura, cv2.TM_SQDIFF_NORMED)
    corresponderPedra = cv2.matchTemplate(imgGray, templatePedra, cv2.TM_SQDIFF_NORMED)

    minCorrespondePapel, _, posicaoCorrespondePapel, _ = cv2.minMaxLoc(correspondePapel)
    minCorrespondeTesoura, _, posicaoCorrespondeTesoura, _ = cv2.minMaxLoc(correspondeTesoura)
    minCorresponderPedra, _, posicaocorresponderPedra, _ = cv2.minMaxLoc(corresponderPedra)

    _, alturaTemplatePapel = templatePapel.shape[::-1]
    _, alturaTemplateTesoura = templateTesoura.shape[::-1]
    _, alturaTemplatePedra = templatePedra.shape[::-1]
    
    if minCorrespondePapel <acharPapel:
        desenharPosicao = (posicaoCorrespondePapel[0] , posicaoCorrespondePapel[1] + alturaTemplatePapel + 30)
        mostrarNaTela(imgRgb, papel, desenharPosicao, cor)
        return [papel, posicaoCorrespondePapel]
    elif minCorrespondeTesoura < acharTesoura:
        desenharPosicao = (posicaoCorrespondeTesoura[0] , posicaoCorrespondeTesoura[1] + alturaTemplateTesoura + 30)
        mostrarNaTela(imgRgb, tesoura, desenharPosicao, cor)
        return [tesoura, posicaoCorrespondeTesoura]
    elif minCorresponderPedra < acharPedra: 
        desenharPosicao = (posicaocorresponderPedra[0] , posicaocorresponderPedra[1] + alturaTemplatePedra + 30)
        mostrarNaTela(imgRgb, pedra, desenharPosicao, cor)
        return [pedra, posicaocorresponderPedra]
    else:
        return [movNaoIdentificado, [0, 0]]

# Função para identificar o termino da rodada e guardar as jogadas anteriores
def novaRodada(jogada1, jogada2):
    global ultimajogada1
    global ultimajogada2

    if jogada1 != ultimajogada1 or jogada2 != ultimajogada2:
        ultimajogada1 = jogada1
        ultimajogada2 = jogada2
        return True
    
    return False

# Funçã para identificar o vencedor da rodada e contabilizar no placar
def score(moverjogador1, moverjogador2):

    if (moverjogador1 == tesoura and moverjogador2 == papel) or \
        (moverjogador1 == papel and moverjogador2 == pedra) or \
        (moverjogador1 == pedra and moverjogador2 == tesoura):
        placar[0] += 1
        verPlacar = str("Placar: ") + str(placar)
        return  ["O Jogador 1 venceu!!!", verPlacar]
    elif (moverjogador1 == papel and moverjogador2 == tesoura) or \
        (moverjogador1 == pedra and moverjogador2 == papel) or \
        (moverjogador1 == tesoura and moverjogador2 == pedra):
        placar[1] += 1
        verPlacar = str("Placar: ") + str(placar)
        return ["O Jogador 2 venceu!!!", verPlacar]
    else:
        verPlacar = str("Placar: ") + str(placar)
        return ["Empate na rodada", verPlacar]

# Função que identifica o video e as jogadas e apresenta os resultados
def video(img):
    global ultimoJogadorVence
    global ultimoPlacar

# Resise da imagem + escala de cinza
    imgScaled = cv2.resize(img, (0, 0), None, 0.400, 0.400)
    imgGray = cv2.cvtColor(imgScaled, cv2.COLOR_BGR2GRAY)

# Largura final da imagem após recise
    imgWidth = imgScaled.shape[1]

# Identificar as jogadas de cada jogador
    movePlayLeft, matchPositionLeft = movimento(imgGray, imgScaled, templatePapel, templateTesoura, templatePedra)
    movePlayRight, matchPositionRight = movimento(imgGray, imgScaled, reverterTemplatePapel, reverterTemplateTesoura, reverterTemplatePedra)

# Idendifica o inicio de uma nova rodada
    isNovaRodada = novaRodada(movePlayLeft, movePlayRight)
        
    if isNovaRodada:
        playerWin, scoreView = score(movePlayLeft, movePlayRight)
        ultimoJogadorVence = playerWin
        ultimoPlacar = scoreView

# Impressão em tela das informações da rodada e placar
    mostrarNaTela(imgScaled, ultimoPlacar, (int(imgWidth / 2) - 120, 20), cor)
    mostrarNaTela(imgScaled, ultimoJogadorVence, (int(imgWidth / 2) - 190, 90), cor)
    mostrarNaTela(imgScaled, jogador1, (matchPositionLeft[0], (matchPositionLeft[1] - 30)), cor)
    mostrarNaTela(imgScaled, jogador2, (matchPositionRight[0], (matchPositionRight[1] - 30)), cor)
        
    return imgScaled

# Atribuir o video a uma variável
videoCap = cv2.VideoCapture("videos/pedrapapeltesoura.mp4")

if videoCap.isOpened():
    rval, frame = videoCap.read()
else:
    rval = False

while rval:
    
    img = video(frame)

    cv2.imshow("checkpoint02", img)

    rval, frame = videoCap.read()
    key = cv2.waitKey(20)
    if key == 27:
        break

cv2.destroyWindow("checkpoint02")
videoCap.release()