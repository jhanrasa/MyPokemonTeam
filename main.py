# --- As Ferramentas que Vamos Usar ---
import sys  # Para interagir com o sistema (como fechar a app)
import os   # Para verificar se as pastas e ficheiros (como os sprites) existem
import random # Para tomar decisões aleatórias (como para onde andar)
import time # Para controlar o tempo (ex: quanto tempo ficar zangado)

# --- As "Peças" Visuais do PyQt5 ---
# Importamos todos os componentes visuais que formam o nosso programa
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, 
                             QGroupBox, QCheckBox, QPushButton, QTextEdit, QHBoxLayout,
                             QScrollArea, QFormLayout, QMessageBox)
from PyQt5.QtGui import QPixmap  # Para carregar e mostrar as imagens (sprites)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal # Para temporizadores, posições (x,y) e sinais

# ==============================================================================
# --- O NOSSO PAINEL DE CONTROLO (Configurações Globais) ---
# ==============================================================================
# Pense nisto como o menu de "Opções" do nosso programa.
# Mudar valores aqui afeta todo o comportamento.

SCREEN_WIDTH = 1920         # A largura do seu ecrã (para o "mundo" transparente)
SCREEN_HEIGHT = 1080        # A altura do seu ecrã
DEFAULT_POKEMON_SIZE = 128  # Tamanho padrão (em pixels) se um Pokémon não tiver tamanho definido
MAX_POKEMON = 6             # Quantos Pokémon podem estar no ecrã ao mesmo tempo
ANIMATION_SPEED = 200       # Velocidade da animação (em milissegundos). Menor = mais rápido
UPDATE_INTERVAL = 100       # Com que frequência o "cérebro" do Pokémon pensa (em ms)
SPRITE_BASE_PATH = "SpriteS" # O nome da pasta onde estão todas as imagens
POKEMON_LIST = [            # A lista "mestra" de todos os Pokémon que o programa conhece
    "Meltan", "Melmetal", "Bulbasaur", "Ivysaur", "Venusaur",
    "Totodile", "Croconaw", "Feraligatr", "Squirtle","Charmander","Charizard"
]

# ==============================================================================
# --- O "DNA" E "PERSONALIDADE" DE CADA POKÉMON ---
# ==============================================================================
# Aqui definimos as características únicas de cada um.
# Se um Pokémon da POKEMON_LIST não estiver aqui, ele usará valores padrão.
POKEMON_PROPERTIES = {
    # can_fly: Consegue voar (ignora a gravidade)
    # mischief: Quão traquinas ele é (0.0 = anjo, 1.0 = demónio)
    # bravery: Coragem (chance de fugir vs. ficar zangado)
    # sociability: Quão social ele é (chance de cumprimentar amigos)
    # max_energy: Quanto tempo fica acordado
    # size: O tamanho individual (em pixels)
    
    "Bulbasaur": {"can_fly": False, "mischief": 0.2, "bravery": 0.6, "sociability": 0.7, "max_energy": 100, "size": 50},
    "Ivysaur": {"can_fly": False, "mischief": 0.3, "bravery": 0.7, "sociability": 0.6, "max_energy": 120, "size": 100},
    "Venusaur": {"can_fly": False, "mischief": 0.4, "bravery": 0.8, "sociability": 0.5, "max_energy": 160, "size": 210},
    "Charmander": {"can_fly": False, "mischief": 0.4, "bravery": 0.7, "sociability": 0.6, "max_energy": 120, "size": 60},
    "Charizard": {"can_fly": True, "mischief": 0.3, "bravery": 0.8, "sociability": 0.4, "max_energy": 180, "size": 170},
    "Squirtle": {"can_fly": False, "mischief": 0.5, "bravery": 0.6, "sociability": 0.6, "max_energy": 110, "size": 50},
    "Totodile": {"can_fly": False, "mischief": 0.7, "bravery": 0.5, "sociability": 0.8, "max_energy": 130, "size": 50},
    "Croconaw": {"can_fly": False, "mischief": 0.6, "bravery": 0.6, "sociability": 0.7, "max_energy": 150, "size": 80},
    "Feraligatr": {"can_fly": False, "mischief": 0.5, "bravery": 0.7, "sociability": 0.6, "max_energy": 200, "size": 200},
    "Meltan": {"can_fly": False, "mischief": 0.1, "bravery": 0.4, "sociability": 0.5, "max_energy": 90, "size": 30},
    "Melmetal": {"can_fly": False, "mischief": 0.1, "bravery": 0.9, "sociability": 0.7, "max_energy": 250, "size": 220},
}

# Este 'loop' é um ajudante.
# Ele verifica se algum Pokémon da POKEMON_LIST ficou sem "Personalidade".
# Se sim, dá-lhe um conjunto de valores padrão (incluindo o DEFAULT_POKEMON_SIZE).
for name in POKEMON_LIST:
    if name not in POKEMON_PROPERTIES:
        POKEMON_PROPERTIES[name] = {"can_fly": False, "mischief": 0.3, "bravery": 0.5, "sociability": 0.5, "max_energy": 100, "size": DEFAULT_POKEMON_SIZE }

# ==============================================================================
# ==== A "ALMA" DO POKÉMON (A Classe Principal) ====
# ==============================================================================
# Esta classe é o "molde" para criar cada Pokémon individual.
# Contém tudo: como se move, como se sente, as imagens, etc.

class Pokemon(QWidget):
    # --- O "Nascimento" do Pokémon ---
    # Esta função é chamada sempre que um novo Pokémon é criado.
    def __init__(self, name, parent_window, start_pos):
        super().__init__(parent_window) # Configuração técnica do PyQt
        self.name = name                 # O nome, ex: "Bulbasaur"
        self.parent_window = parent_window # A referência ao "mundo" (o ecrã)
        
        # Pega as "personalidades" definidas lá em cima
        self.properties = POKEMON_PROPERTIES.get(name, {}) 
        
        # Define características com base nessas propriedades
        self.can_fly = self.properties.get("can_fly", False)
        
        # Pega o tamanho individual. Se não tiver um, usa o tamanho padrão.
        self.size = self.properties.get("size", DEFAULT_POKEMON_SIZE)

        # --- Variáveis para Arrastar ---
        self.is_dragging = False      # Está a ser arrastado pelo rato?
        self.drag_position = QPoint(0, 0) # Posição do rato relativa ao canto do Pokémon

        # --- "Guarda-Roupa" de Animações ---
        # Um dicionário que vai guardar todas as imagens (frames) para cada ação
        self.sprites = {
            'idle': [], 'walk': [], 'greet': [], 'happy': [],
            'angry': [], 'scared': [], 'sleepy': [], 'naughty': [],
            'fly_idle': [], 'fly_walk': []
        }
        self.current_animation = 'idle' # Animação atual (começa parado)
        self.current_frame = 0          # O fotograma (frame) atual da animação
        self.label = QLabel(self)       # O "ecrã" que mostra a imagem do Pokémon
        
        self.load_sprites() # Chama a função para "encher o guarda-roupa"

        # --- Estados e Comportamento ---
        self.state = 'idle'            # O estado mental (ex: 'walking', 'sleepy')
        self.target_pos = None         # Para onde ele quer ir
        self.friendships = {}          # Dicionário para guardar o nível de amizade com outros
        self.happiness = 50            # Nível de felicidade
        self.anger = 0                 # Nível de raiva
        
        # Energia (para o ciclo de sono)
        self.max_energy = self.properties.get("max_energy", 100)
        self.energy = self.max_energy
        
        # "Temporizadores" para emoções (medidos em segundos 'time.time()')
        self.scared_timeout = 0 # Até quando ficará assustado
        self.angry_timeout = 0  # Até quando ficará zangado
        self.action_timeout = 0 # Até quando fará a próxima ação
        self.angry_target = None # De quem ele está zangado

        # --- Plano B (Se Faltarem Imagens) ---
        # Se, após carregar, ele não tiver NENHUMA imagem, cria um quadrado azul
        if not self.sprites['idle'] and not self.sprites['fly_idle']:
             pm = QPixmap(self.size, self.size) # Usa o tamanho individual!
             pm.fill(Qt.cyan)
             self.sprites['idle'].append(pm)

        # Define a animação inicial (voando ou parado no chão)
        self.current_animation = 'fly_idle' if self.can_fly and self.sprites['fly_idle'] else 'idle'
        self.set_animation(self.current_animation)

        # Define a geometria (posição e tamanho) inicial. Usa o self.size!
        self.setGeometry(start_pos.x(), start_pos.y(), self.size, self.size)
        
        self.update_sprite() # Mostra o primeiro fotograma
        self.show() # Torna o Pokémon visível

        # --- O "Coração" do Pokémon ---
        # Um temporizador que chama 'update_behavior' (o "cérebro")
        # várias vezes por segundo (definido em UPDATE_INTERVAL)
        self.behavior_timer = QTimer(self)
        self.behavior_timer.timeout.connect(self.update_behavior)
        self.behavior_timer.start(UPDATE_INTERVAL)
        
    # --- Interação: Agarrar o Pokémon ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.state = 'held' # Estado "a ser segurado"
            
            # Pega nas suas personalidades
            sociability = self.properties.get("sociability", 0.5)
            bravery = self.properties.get("bravery", 0.5)

            # Decide como reagir a ser agarrado
            if sociability > 0.6 or bravery > 0.7:
                self.set_animation('happy') # Pokémon corajosos/sociais gostam
                self.happiness = min(100, self.happiness + 2)
            elif bravery < 0.4:
                self.set_animation('scared') # Pokémon medrosos assustam-se
            elif sociability < 0.4:
                self.set_animation('angry') # Pokémon antissociais zangam-se
            else:
                self.set_animation('idle') # Neutros

            self.drag_position = event.globalPos() - self.pos()
            event.accept()

    # --- Interação: Arrastar o Pokémon ---
    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    # --- Interação: Largar o Pokémon ---
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.set_state_idle() # Volta ao estado normal (parado)
            event.accept()
            
    # --- Carregar o "Guarda-Roupa" ---
    def load_sprites(self):
        pokemon_path = os.path.join(SPRITE_BASE_PATH, self.name)
        if not os.path.isdir(pokemon_path):
            # Se não encontrar a pasta do Pokémon, pára
            return
            
        # Itera por todas as animações (idle, walk, etc.)
        for anim_type in self.sprites.keys():
            anim_path = os.path.join(pokemon_path, anim_type)
            if os.path.isdir(anim_path):
                i = 0
                while True: # Loop infinito até não encontrar mais imagens
                    sprite_file = os.path.join(anim_path, f"{anim_type}_{i}.png")
                    if os.path.exists(sprite_file):
                        pixmap = QPixmap(sprite_file)
                        if not pixmap.isNull():
                           # AQUI! Redimensiona a imagem para o tamanho individual
                           scaled_pixmap = pixmap.scaled(self.size, self.size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                           self.sprites[anim_type].append(scaled_pixmap) # Adiciona ao "guarda-roupa"
                        i += 1
                    else:
                        break # Pára o 'while' quando não houver mais imagens (ex: 'walk_3.png')
    
    # --- Mudar a Animação Atual ---
    def set_animation(self, anim_name):
        # Verifica se a animação pedida existe E tem imagens
        if anim_name in self.sprites and self.sprites[anim_name]:
            if self.current_animation != anim_name:
                self.current_animation = anim_name
                self.current_frame = 0 # Reinicia a contagem de fotogramas
        # Se a animação pedida não existir...
        elif self.can_fly:
             self.current_animation = 'fly_idle' # Tenta voar parado
        else:
            self.current_animation = 'idle' # Fica parado no chão
            
        # Se, mesmo assim, a animação padrão (idle/fly_idle) não tiver imagens...
        if not self.sprites[self.current_animation]:
             self.current_animation = 'idle' # Força 'idle' como último recurso
             if not self.sprites['idle']: return # Se nem 'idle' existir, desiste.
        self.current_frame = 0

    # --- Atualizar o Fotograma (Frame) ---
    # Esta função é chamada pelo temporizador GERAL (update_animations)
    def update_sprite(self):
        anim_list = self.sprites.get(self.current_animation)
        if anim_list:
            # Avança para o próximo fotograma, ou volta ao início (looping)
            self.current_frame = (self.current_frame + 1) % len(anim_list)
            pixmap = anim_list[self.current_frame]
            self.label.setPixmap(pixmap) # Mostra a imagem
            self.label.setMask(pixmap.mask()) # Para fundos transparentes
            self.label.adjustSize()
            self.setFixedSize(self.label.size())

    # --- O "CÉREBRO" (Função Principal de Decisão) ---
    # Esta função é chamada várias vezes por segundo (pelo behavior_timer)
    def update_behavior(self):
        # Se estiver a ser arrastado, não faz nada
        if self.is_dragging:
            return

        # --- Gestão de Energia (Ciclo de Sono) ---
        if self.state != 'sleepy':
            self.energy -= 0.1 # Gasta energia lentamente
            if self.energy <= 0:
                self.energy = 0
                self.state = 'sleepy'
                self.set_animation('sleepy')
                self.target_pos = None # Pára de andar
        else:
            self.energy += 0.4 # Recupera energia a dormir
            if self.energy >= self.max_energy:
                self.energy = self.max_energy
                self.set_state_idle() # Acorda!
            return # Se está a dormir, não faz mais nada

        # --- Gestão de Emoções (Temporizadores) ---
        current_time = time.time() # Pega na hora atual
        
        # Está assustado?
        if self.scared_timeout > current_time:
            self.state = 'scared'
            self.run_scared() # Foge!
            return # Se está assustado, não faz mais nada
        elif self.state == 'scared':
            self.set_state_idle() # O tempo de susto acabou

        # Está zangado?
        if self.angry_timeout > current_time:
            self.state = 'angry'
            self.move_randomly(fast=True) # Anda erraticamente
            return # Se está zangado, não faz mais nada
        elif self.state == 'angry':
            self.set_state_idle() # O tempo de raiva acabou
            self.angry_target = None
        
        # --- Decidir uma Nova Ação ---
        # Se o "temporizador de ação" acabou, decide algo novo
        if self.action_timeout < current_time:
            # Define um novo temporizador (entre 3 a 10 segundos)
            self.action_timeout = current_time + random.uniform(3, 10)
            
            # Chance de fazer uma travessura (baseado na personalidade)
            if random.random() < self.properties.get("mischief", 0.3) / 10:
                 self.try_mischief()
                 return

            # Chance de ficar feliz (baseado na felicidade)
            if random.random() < self.happiness / 200:
                self.state = 'happy'
                self.set_animation('happy')
                # Fica feliz por 3 segundos, depois volta ao normal
                QTimer.singleShot(3000, self.set_state_idle)
                return

            # Se não fez nada disso, decide se vai andar ou ficar parado
            self.decide_move()

        # --- Executar Ações ---
        # Se o estado atual é "a andar", continua a mover-se
        if self.state in ['walking', 'fly_walk']:
            self.move_towards_target()
        
        # Verifica se há amigos por perto
        self.check_nearby_pokemon()
    
    # --- "Relaxar" ---
    def set_state_idle(self):
        # Só relaxa se não estiver num estado "importante" (assustado, zangado, etc.)
        if self.state not in ['scared', 'angry', 'sleepy']:
             self.state = 'idle'
             anim = 'fly_idle' if self.can_fly else 'idle' # Voa parado ou fica parado
             if not self.sprites[anim]:
                 anim = 'idle'
             self.set_animation(anim)

    # --- Decidir Passear ---
    def decide_move(self):
        if self.state not in ['idle', 'fly_idle']: return # Só decide se estiver parado
        
        # 50% de chance de decidir andar
        if random.choice([True, False]):
            self.state = 'fly_walk' if self.can_fly and self.sprites['fly_walk'] else 'walking'
            self.set_animation(self.state)
            
            if self.can_fly:
                # Se voa, escolhe qualquer ponto no ecrã
                self.target_pos = QPoint(random.randint(0, self.parent_window.width() - self.width()), random.randint(0, self.parent_window.height() - self.height()))
            else:
                # Se não voa, fica na metade de baixo do ecrã ("chão")
                ground_level_start = self.parent_window.height() // 2
                self.target_pos = QPoint(random.randint(0, self.parent_window.width() - self.width()), random.randint(ground_level_start, self.parent_window.height() - self.height()))
        else:
            # 50% de chance de ficar parado
            self.state = 'fly_idle' if self.can_fly else 'idle'
            self.set_animation(self.state)
            self.target_pos = None

    # --- "Caminhar" (Mover-se para o Alvo) ---
    def move_towards_target(self):
        if not self.target_pos: # Se não tem alvo, pára
            self.set_state_idle()
            return
            
        current_pos = self.pos()
        dx = self.target_pos.x() - current_pos.x() # Distância X
        dy = self.target_pos.y() - current_pos.y() # Distância Y
        distance = (dx**2 + dy**2)**0.5 # Teorema de Pitágoras
        
        if distance < 15: # Se chegou perto o suficiente
            self.target_pos = None
            self.set_state_idle()
        else:
            step = 3 # Velocidade de caminhada
            # Calcula o próximo movimento
            move_x = int(step * dx / distance) if distance != 0 else 0
            move_y = int(step * dy / distance) if distance != 0 else 0
            
            new_x = max(0, min(current_pos.x() + move_x, self.parent_window.width() - self.width()))
            new_y = max(0, min(current_pos.y() + move_y, self.parent_window.height() - self.height()))
            
            # "Gravidade" (se não voa, não sobe acima de 1/3 do ecrã)
            if not self.can_fly and self.state != 'scared':
                ground_limit = self.parent_window.height() // 3
                new_y = max(new_y, ground_limit)
                
            self.move(new_x, new_y)

    # --- "Fugir" (Movimento Rápido de Susto) ---
    def run_scared(self):
        if not self.target_pos: # Se não tem alvo de fuga, escolhe um canto
            self.target_pos = QPoint(random.choice([0, self.parent_window.width() - self.width()]), random.choice([0, self.parent_window.height() - self.height()]))
            self.set_animation('scared')
            
        current_pos = self.pos()
        dx = self.target_pos.x() - current_pos.x()
        dy = self.target_pos.y() - current_pos.y()
        distance = (dx**2 + dy**2)**0.5
        
        if distance < 30: # Chegou ao canto
            self.target_pos = None
        else:
            step = 10 # Velocidade de fuga (mais rápido que 'step = 3')
            move_x = int(step * dx / distance) if distance != 0 else 0
            move_y = int(step * dy / distance) if distance != 0 else 0
            new_x = max(0, min(current_pos.x() + move_x, self.parent_window.width() - self.width()))
            new_y = max(0, min(current_pos.y() + move_y, self.parent_window.height() - self.height()))
            self.move(new_x, new_y)

    # --- Movimento Errático (Quando Zangado) ---
    def move_randomly(self, fast=False):
        step = 8 if fast else 4 # Zangado (fast) move-se mais
        current_pos = self.pos()
        new_x = current_pos.x() + random.randint(-step, step)
        new_y = current_pos.y() + random.randint(-step, step)
        
        # Limita ao ecrã
        new_x = max(0, min(new_x, self.parent_window.width() - self.width()))
        new_y = max(0, min(new_y, self.parent_window.height() - self.height()))
        
        if not self.can_fly: # Respeita o "chão"
             new_y = max(new_y, self.parent_window.height() // 3)
        self.move(new_x, new_y)

    # --- "Ver Amigos" (Interação Social) ---
    def check_nearby_pokemon(self):
        # Se estiver ocupado (assustado, a dormir, etc.) não interage
        if self.state in ['scared', 'angry', 'sleepy', 'greeting', 'held']:
            return
            
        # Vê todos os outros Pokémon no ecrã
        for other_poke in self.parent_window.pokemon_widgets:
            if other_poke == self: continue # Ignora-se a si mesmo
            
            # AQUI! A distância de interação é baseada no tamanho dos dois
            interaction_distance = (self.size + other_poke.size) / 2 
            
            # Calcula a distância entre os centros
            distance = QPoint(self.geometry().center() - other_poke.geometry().center()).manhattanLength()
            
            if distance < interaction_distance: # Se estiverem perto
                friend_level = self.friendships.get(other_poke.name, 0.5)
                
                # --- Reação Boa (Cumprimentar) ---
                if friend_level > 0.3 and self.state in ['idle', 'fly_idle'] and other_poke.state in ['idle', 'fly_idle']:
                    # Se forem amigos, e ambos estiverem parados, e for sociável...
                    if random.random() < self.properties.get("sociability", 0.5):
                        self.start_greeting(other_poke)
                        other_poke.start_greeting(self)
                        self.update_friendship(other_poke.name, 0.05) # Aumenta amizade
                        other_poke.update_friendship(self.name, 0.05)
                        return
                        
                # --- Reação Má (Fugir ou Zangar-se) ---
                if friend_level < 0.2 or other_poke.state == 'angry':
                    # Se não forem amigos, ou o outro estiver zangado...
                    if random.random() > self.properties.get("bravery", 0.5):
                        self.get_scared(source=other_poke) # Medroso: foge
                    else:
                        self.get_angry(target=other_poke) # Corajoso: zanga-se
                    return

    # --- Ação: Cumprimentar ---
    def start_greeting(self, other_poke):
        if self.state != 'greeting':
            self.state = 'greeting'
            self.set_animation('greet')
            self.target_pos = None # Pára de andar para cumprimentar
            QTimer.singleShot(3000, self.set_state_idle) # Fica 3s a cumprimentar

    # --- Emoção: Ficar Assustado ---
    def get_scared(self, source=None, duration=5):
        self.state = 'scared'
        self.set_animation('scared')
        self.scared_timeout = time.time() + duration # Fica assustado por 5s
        self.target_pos = None # Pára (para 'run_scared' escolher um alvo)
        if source:
             self.update_friendship(source.name, -0.2) # Gosta menos de quem o assustou

    # --- Emoção: Ficar Zangado ---
    def get_angry(self, target=None, duration=7):
        self.state = 'angry'
        self.set_animation('angry')
        self.angry_timeout = time.time() + duration # Fica zangado por 7s
        self.angry_target = target
        self.target_pos = None
        if target:
            self.update_friendship(target.name, -0.1) # Gosta menos do alvo

    # --- Ação: Tentar Travessura ---
    def try_mischief(self):
        if self.state not in ['idle', 'fly_idle']: return
        # Encontra alvos fáceis (que não estejam assustados ou zangados)
        targets = [p for p in self.parent_window.pokemon_widgets if p != self and p.state not in ['scared', 'angry']]
        if not targets: return
        
        target_poke = random.choice(targets) # Escolhe uma vítima
        self.state = 'naughty'
        self.set_animation('naughty')
        self.target_pos = target_poke.pos() # Anda em direção à vítima
        # Daqui a 4 segundos, executa a travessura
        QTimer.singleShot(4000, lambda: self.execute_mischief(target_poke))

    # --- Ação: Executar Travessura ---
    def execute_mischief(self, target):
         if self.state == 'naughty': # Confirma que ainda está em modo "traquina"
            target.get_scared(source=self) # Assusta o alvo!
            self.state = 'happy' # Fica feliz com a maldade
            self.set_animation('happy')
            self.update_friendship(target.name, -0.1) # O alvo gosta menos dele
            QTimer.singleShot(2000, self.set_state_idle) # Fica feliz por 2s

    # --- Memória: Atualizar Amizades ---
    def update_friendship(self, name, change):
        current_level = self.friendships.get(name, 0.5)
        # O nível de amizade fica sempre entre 0.0 (ódio) e 1.0 (melhores amigos)
        self.friendships[name] = max(0.0, min(1.0, current_level + change))

# ==============================================================================
# ==== O "CARTÃO DE STATUS" (Para a Janela de Configuração) ====
# ==============================================================================
# Este é o pequeno widget que aparece na janela de Config (Ctrl+O)
# para mostrar o estado de CADA Pokémon.
class PokemonStatusWidget(QGroupBox):
    def __init__(self, pokemon):
        super().__init__(pokemon.name) # O título do "card" é o nome
        self.pokemon_name = pokemon.name
        
        self.layout = QFormLayout(self)
        
        # Cria as etiquetas (labels) para mostrar a informação
        self.state_label = QLabel(pokemon.state)
        self.energy_label = QLabel(f"{int(pokemon.energy)} / {pokemon.max_energy}")
        self.happiness_label = QLabel(str(pokemon.happiness))
        self.friendships_label = QLabel("Nenhuma")
        self.friendships_label.setWordWrap(True) # Permite quebra de linha
        
        # Adiciona as etiquetas ao "card"
        self.layout.addRow("Estado:", self.state_label)
        self.layout.addRow("Energia:", self.energy_label)
        self.layout.addRow("Felicidade:", self.happiness_label)
        self.layout.addRow("Amizades:", self.friendships_label)
        
        self.update_stats(pokemon) # Popula os dados pela primeira vez

    # Esta função é chamada pelo temporizador da ConfigWindow para atualizar os dados
    def update_stats(self, pokemon):
        self.state_label.setText(pokemon.state)
        self.energy_label.setText(f"{int(pokemon.energy)} / {pokemon.max_energy}")
        self.happiness_label.setText(str(pokemon.happiness))
        
        # Formata a lista de amigos
        friend_text = ", ".join([f"{name}: {level:.2f}" for name, level in pokemon.friendships.items()])
        if not friend_text:
            friend_text = "Nenhuma"
        self.friendships_label.setText(friend_text)

# ==============================================================================
# ==== A "JANELA DE OPÇÕES" (Atalho: Ctrl+O) ====
# ==============================================================================
class ConfigWindow(QWidget):
    # "Sinais" que a janela envia para o "Mundo" (DesktopPetApp)
    pokemon_selection_changed = pyqtSignal(list) # Avisa quando clicamos "Aplicar"
    close_app_signal = pyqtSignal() # Avisa quando clicamos "Fechar Programa"

    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app # Referência ao "Mundo"
        self.setWindowTitle("Configurações")
        self.setWindowFlag(Qt.WindowStaysOnTopHint) # Fica sempre por cima
        self.setGeometry(100, 100, 450, 700) # Posição e tamanho da janela

        self.main_layout = QVBoxLayout(self)
        
        # --- Seção de Seleção de Pokémon ---
        self.selection_groupbox = QGroupBox(f"Selecionar Pokémon (Máximo: {MAX_POKEMON})")
        self.selection_layout = QVBoxLayout()
        self.checkboxes = []
        for name in POKEMON_LIST:
            checkbox = QCheckBox(name)
            # Verifica se este Pokémon já está ativo para marcar a caixa
            if any(p.name == name for p in self.parent_app.pokemon_widgets):
                 checkbox.setChecked(True)
            self.checkboxes.append(checkbox)
            self.selection_layout.addWidget(checkbox)
        self.selection_groupbox.setLayout(self.selection_layout)
        
        # --- Seção de Status (com scroll) ---
        self.status_groupbox = QGroupBox("Status dos Pokémon Ativos")
        status_container_widget = QWidget() # Widget "interior" para o scroll
        self.status_layout = QVBoxLayout(status_container_widget)
        self.status_layout.setAlignment(Qt.AlignTop) # Alinha os "cards" no topo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(status_container_widget)
        status_group_layout = QVBoxLayout(self.status_groupbox)
        status_group_layout.addWidget(scroll_area) # Adiciona a área de scroll à secção
        self.status_widgets = {} # Dicionário para guardar os "cards" de status

        # --- Seção de Botões ---
        self.button_layout = QHBoxLayout()
        self.apply_button = QPushButton("Aplicar")
        self.apply_button.clicked.connect(self.apply_changes)
        self.close_button = QPushButton("Fechar Programa")
        self.close_button.clicked.connect(self.close_app_signal.emit)
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.close_button)

        # Adiciona as 3 secções à janela principal
        self.main_layout.addWidget(self.selection_groupbox)
        self.main_layout.addWidget(self.status_groupbox)
        self.main_layout.addLayout(self.button_layout)
        
        # Temporizador para atualizar os "cards" de status
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000) # Atualiza a cada 1 segundo

    # --- O que acontece ao clicar "Aplicar" ---
    def apply_changes(self):
        # Cria uma lista com os nomes de quem foi marcado
        selected_pokemon_names = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        
        # AQUI! Verifica se o utilizador não escolheu mais que o limite
        if len(selected_pokemon_names) > MAX_POKEMON:
            # Mostra uma janela de aviso
            QMessageBox.warning(self, "Limite Excedido", f"Você só pode selecionar no máximo {MAX_POKEMON} Pokémon.")
            return # Pára a função aqui. Não aplica as mudanças.

        # Se passou na verificação, emite o sinal para o "Mundo"
        self.pokemon_selection_changed.emit(selected_pokemon_names)
        self.hide() # Esconde a janela de opções

    # --- Atualizar os "Cards" de Status ---
    def update_status_display(self):
        # Se a janela não estiver visível, poupa recursos e não faz nada
        if not self.isVisible():
            return
            
        # Mapeia os Pokémon ativos pelo nome
        active_pokemon_map = {p.name: p for p in self.parent_app.pokemon_widgets}
        active_names = set(active_pokemon_map.keys())
        widget_names = set(self.status_widgets.keys()) # Nomes dos "cards" que já existem

        # Adiciona "cards" para Pokémon que acabaram de ser criados
        for name in active_names - widget_names:
            widget = PokemonStatusWidget(active_pokemon_map[name])
            self.status_layout.addWidget(widget)
            self.status_widgets[name] = widget

        # Remove "cards" de Pokémon que foram dispensados
        for name in widget_names - active_names:
            widget_to_remove = self.status_widgets.pop(name)
            widget_to_remove.deleteLater() # Remove o widget da memória

        # Atualiza os "cards" que continuam ativos
        for name, widget in self.status_widgets.items():
            if name in active_pokemon_map:
                widget.update_stats(active_pokemon_map[name])

# ==============================================================================
# ==== O "MUNDO" (A Aplicação Principal) ====
# ==============================================================================
# Esta é a classe principal que gere tudo.
# É a janela transparente do tamanho do ecrã onde os Pokémon vivem.
class DesktopPetApp(QWidget):
    def __init__(self):
        super().__init__()
        self.pokemon_widgets = [] # A lista de todos os Pokémon ativos no ecrã
        
        # --- Configuração da Janela Transparente ---
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground) # Magia! Torna o fundo transparente
        self.setGeometry(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT) # Ocupa o ecrã todo

        # --- O "Maestro" da Animação ---
        # Este temporizador é GERAL. Ele diz a TODOS os Pokémon
        # para avançarem um fotograma (frame) da sua animação.
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(ANIMATION_SPEED) # Usa a velocidade global

        # --- Cria a Janela de Configuração ---
        self.config_window = ConfigWindow(self)
        # "Ouve" os sinais que a janela de configuração envia
        self.config_window.pokemon_selection_changed.connect(self.update_active_pokemon)
        self.config_window.close_app_signal.connect(QApplication.instance().quit)
        
        # Pokémon iniciais (pode mudar isto!)
        initial_pokemon = ["Totodile", "Charmander", "Bulbasaur"]
        self.update_active_pokemon(initial_pokemon)

    # --- O Atalho Secreto (Ctrl+O) ---
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_O and event.modifiers() == Qt.ControlModifier:
            if self.config_window.isVisible():
                self.config_window.hide()
            else:
                # Antes de mostrar, atualiza as checkboxes
                # para refletir quem está no ecrã
                for cb in self.config_window.checkboxes:
                    is_active = any(p.name == cb.text() for p in self.pokemon_widgets)
                    cb.setChecked(is_active)
                self.config_window.show()
                self.config_window.activateWindow() # Traz a janela para a frente

    # --- O "Gerente" (Adiciona/Remove Pokémon) ---
    # Chamado quando clicamos "Aplicar" na janela de config.
    def update_active_pokemon(self, selected_names):
        current_names = {p.name for p in self.pokemon_widgets}
        
        # Remove Pokémon que foram desmarcados
        for poke in list(self.pokemon_widgets):
            if poke.name not in selected_names:
                poke.deleteLater() # Apaga o widget
                self.pokemon_widgets.remove(poke) # Remove da lista
        
        # Adiciona Pokémon que foram marcados
        for name in selected_names:
            if name not in current_names:
                self.add_pokemon(name)
        
        # Faz com que todos os Pokémon se "conheçam" (para as amizades)
        self.initialize_friendships()

    # --- A "Porta de Entrada" (Cria um Pokémon) ---
    def add_pokemon(self, name):
        # AQUI! Lê as propriedades e o tamanho ANTES de criar
        properties = POKEMON_PROPERTIES.get(name, {})
        size = properties.get("size", DEFAULT_POKEMON_SIZE)

        # Calcula uma posição inicial aleatória, garantindo que cabe no ecrã
        start_x = random.randint(0, self.width() - size)
        start_y = random.randint(self.height() // 2, self.height() - size)
        
        # "Nasce" o Pokémon! (Chama o __init__ da classe Pokemon)
        new_poke = Pokemon(name, self, QPoint(start_x, start_y))
        self.pokemon_widgets.append(new_poke)

    # --- "Apresentações" (Inicializar Amizades) ---
    def initialize_friendships(self):
        all_names = [p.name for p in self.pokemon_widgets]
        for poke in self.pokemon_widgets:
            for name in all_names:
                if name != poke.name and name not in poke.friendships:
                    poke.friendships[name] = 0.5 # Começam todos neutros (0.5)

    # --- O "Maestro" (Diz a todos para se animarem) ---
    def update_animations(self):
        for poke in self.pokemon_widgets:
            poke.update_sprite() # Diz a cada um para avançar um fotograma

# ==============================================================================
# ==== O "BOTÃO DE LIGAR" (A Ignição) ====
# ==============================================================================
# Este código só é executado quando o ficheiro é corrido diretamente.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Verificação de segurança CRÍTICA
    if not os.path.isdir(SPRITE_BASE_PATH):
        print(f"Erro Crítico: A pasta '{SPRITE_BASE_PATH}' não foi encontrada.")
        print("Certifique-se que a pasta com as imagens está no mesmo local que o main.py")
        # (Idealmente, mostraríamos um QMessageBox aqui, mas 'print' é mais simples)
        sys.exit(1) # Pára o programa
    
    # Cria o "Mundo"
    window = DesktopPetApp()
    window.show()
    
    # Entrega o controlo à aplicação
    sys.exit(app.exec_())