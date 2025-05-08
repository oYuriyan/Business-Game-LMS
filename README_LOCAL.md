
# Guia Local para Rodar o Projeto — Business Game

Este documento explica **como iniciar e testar o projeto Business Game localmente**.


### 1. Abrir o projeto no VS Code
Certifique-se de que a pasta `business_game/` está aberta no VS Code.

---

## Dicas
- Sempre ative o ambiente virtual antes de rodar qualquer comando.
- Se trocar de computador, instale tudo com:
  ```bash
  python -m venv venv
  source venv/Scripts/activate
  pip install -r requirements.txt
  ```


### 2. Ativar o ambiente virtual

#### CMD ou PowerShell:
```bash
venv\Scripts\activate
```

#### Git Bash:
```bash
source venv/Scripts/activate
```

---

### 3. (Somente na primeira vez) Instalar as dependências
```bash
pip install -r requirements.txt
```

---

### 4. Aplicar as migrations
```bash
python manage.py migrate
```

Isso cria as tabelas do banco (como `auth_user`, `sessions`, etc.).

---

### 5. Criar um superusuário (para fazer login)
```bash
python manage.py createsuperuser
```

### 6. Iniciar o servidor local
```bash
python manage.py runserver
```

Você verá:
```
Starting development server at http://127.0.0.1:8000/
```

---

### 7. Acessar no navegador
- Login: [http://localhost:8000/login/](http://localhost:8000/login/)
- Dashboard: [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)

---