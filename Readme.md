# Business Game - Simulador de Logística de Mercado (LMS)

![Status do Projeto](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Plataforma](https://img.shields.io/badge/plataforma-web-blue)
![Tecnologia](https://img.shields.io/badge/tecnologia-Django-green)

## Sobre o Projeto

O **Business Game LMS** é uma plataforma web gamificada para simulação de cenários de logística e negócios. [cite_start]O projeto foi concebido como uma ferramenta educacional para oferecer aos alunos uma oportunidade de aprendizado interdisciplinar, permitindo a aplicação prática de conceitos de logística, como o Método de Aproximação de Vogel (MAV) e Simplex. 

[cite_start]Desenvolvido para o curso de Tecnologia em Análise e Desenvolvimento de Sistemas, o jogo digitaliza e expande uma atividade prática aplicada com sucesso desde 2002, impactando centenas de alunos.  [cite_start]Os jogadores assumem o papel de empresas concorrentes, tomando decisões estratégicas sobre produção, estoque, precificação e transporte para atender a uma demanda de mercado variável a cada rodada. 

## Funcionalidades Principais

* [cite_start]**Ambiente Multiplayer:** Partidas com até 4 jogadores competindo em tempo real. 
* [cite_start]**Gerenciamento de Partidas:** O administrador (professor) tem controle total para criar, iniciar, pausar e finalizar partidas. 
* [cite_start]**Simulação por Rodadas:** O jogo avança em rodadas, cada uma com uma nova demanda de produto, quantidade e destino. 
* **Decisões Estratégicas:** Os jogadores devem decidir o quanto produzir e o preço de venda para serem competitivos.
* [cite_start]**Logística de Custos:** Custos de produção e transporte variam para cada empresa, exigindo cálculos precisos para maximizar o lucro. 
* [cite_start]**Sistema de "Pregão":** O sistema simula uma licitação, onde a empresa com o menor preço ganha a venda, desde que tenha estoque. 
* [cite_start]**Resultados e Ranking:** A cada rodada e ao final da partida, são exibidos relatórios de desempenho e um ranking dos jogadores. 

## Tecnologias Utilizadas

* **Back-end:** Python com o framework Django
* **Front-end:** HTML5, CSS, Tailwind CSS, JavaScript
* **Banco de Dados:** SQLite (para desenvolvimento)
* **Arquitetura:** Model-View-Template (MVT)

## Como Rodar o Projeto Localmente

Siga estas instruções para configurar e rodar o ambiente de desenvolvimento.

### Pré-requisitos
* Python 3.8 ou superior
* Git

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd business-game-lms
    ```

2.  **Crie e ative um ambiente virtual:**
    *No Windows (CMD/PowerShell):*
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
    *No macOS/Linux (Bash):*
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário (admin):**
    ```bash
    python manage.py createsuperuser
    ```
    (Siga as instruções para criar seu usuário e senha de administrador.)

6.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

7.  **Acesse a aplicação:**
    * **Página Inicial:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
    * **Login:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
    * **Painel do Admin:** [http://127.0.0.1:8000/painel/](http://127.0.0.1:8000/painel/) (acesse com o superusuário)

## Como Jogar

1.  **Admin:** Faça login com a conta de superusuário e acesse o **Painel Admin**.
2.  **Admin:** Clique em "Criar Nova Partida", defina um nome e o número de rodadas.
3.  **Jogadores:** Criem suas contas na tela de cadastro e façam login.
4.  **Jogadores:** Acessem o **Lobby** e entrem na partida criada pelo admin. Cada jogador receberá uma empresa (A, B, C ou D).
5.  **Admin:** Quando todos os jogadores estiverem na sala, inicie a primeira rodada. Defina o produto, a quantidade e o destino da demanda.
6.  **Jogadores:** Na sala da partida, tomem suas decisões de produção e preço e as confirmem.
7.  **Admin:** Após todos decidirem, avance a rodada. Os resultados serão processados e uma nova rodada começará.
8.  O ciclo se repete até a última rodada. [cite_start]O vencedor é quem tiver o maior saldo ao final. 

## Autores

* Yuri Yan
* Vinicius Soares

Desenvolvido como Projeto de Conclusão de Curso em Análise e Desenvolvimento de Sistemas.