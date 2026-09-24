# 🎮 MyPokemonTeam - Desktop Pokémon Pets Companion

Aplicação interativa para desktop desenvolvida em Python e **PyQt5** que traz seus Pokémons favoritos para passear, interagir, voar e viver diretamente na sua área de trabalho como mascotes virtuais interativos (Desktop Pets / Shimeji).

---

## 🎯 Principais Funcionalidades

- 🐾 **Pokémons Vivos na Tela**:
  - Janelas transparentes e sem bordas que passeiam livremente por cima de quaisquer janelas abertas no Windows.
  - Animações fluidas de *Idle*, caminhada, corrida, sono e reações.
- 🧠 **Sistema de Personalidade e IA Autônoma**:
  - Cada espécie possui parâmetros individuais de temperamento: coragem, travessura, sociabilidade, nível de energia e habilidade de voo.
  - Pokémons voadores (como Charizard) desafiam a gravidade e sobrevoam o monitor.
  - Interações sociais quando dois Pokémons se encontram na tela.
- 🎛️ **Painel de Controle Completo**:
  - Interface visual para selecionar até 6 companheiros simultâneos para a equipe.
  - Controle de velocidade de animação, tamanho e tempo de reação.
- 📦 **Sprites Inclusos**:
  - Bulbasaur, Ivysaur, Venusaur, Charmander, Charizard, Squirtle, Totodile, Croconaw, Feraligatr, Meltan e Melmetal.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.10+**
- **PyQt5** (Janelas transparentes com `Qt.FramelessWindowHint` e `Qt.WindowStaysOnTopHint`, renderização de sprites e eventos)
- **PyInstaller** (Empacotamento em executável `.exe` independente)
- **Pillow** (Processamento e extração de sprites animados)

---

## 🚀 Como Executar

### 1. Clonar o Repositório
```bash
git clone https://github.com/jhanrasa/MyPokemonTeam.git
cd MyPokemonTeam
```

### 2. Criar e Ativar Ambiente Virtual
```bash
python -m venv venv

# No Windows:
.\venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Iniciar a Aplicação
```bash
python main.py
```

### 5. (Opcional) Gerar Executável Windows
```bash
pyinstaller --noconfirm --onedir --windowed --add-data "SpriteS;SpriteS" main.py
```

---

## 📂 Estrutura do Projeto

```
MyPokemonTeam/
├── SpriteS/                     # Folhas de sprites e quadros de animação por Pokémon
│   ├── bulbasaur/idle/
│   ├── charizard/idle/
│   ├── charmander/idle/
│   └── ...
├── main.py                      # Motor principal, inteligência artificial e GUI PyQt5
├── requirements.txt             # Dependências da aplicação
├── .gitignore                   # Exclusão de builds PyInstaller e backups temporários
└── README.md                    # Documentação do projeto
```

---

## 📄 Licença
Distribuído sob a licença MIT. Pokémon e respectivos nomes são marcas registradas da Nintendo / Creatures Inc. / GAME FREAK inc.
