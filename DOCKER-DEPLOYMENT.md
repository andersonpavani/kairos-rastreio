# Deployment com Docker - Kairos Rastreio

Uma alternativa ao deployment manual usando Docker e Docker Compose.

## 🐳 Opção 1: Docker + Docker Compose (RECOMENDADO)

### Pré-requisitos
- Ubuntu 22.04
- Docker instalado
- Docker Compose instalado

### 1. Instalar Docker e Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuario ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Instalar Docker Compose
sudo apt install -y docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

### 2. Preparar arquivos

```bash
# Clone repositório ou copie para seu servidor
cd /home/seu-usuario/kairos-rastreio

# Criar diretório para logs
mkdir -p logs/nginx

# Criar arquivo .env
nano .env
# Adicione:
# SITERASTREIO_TOKEN=seu_token_aqui
# FLASK_ENV=production

chmod 600 .env
```

### 3. Build e Deploy

```bash
# Build da imagem
docker-compose build

# Iniciar containers
docker-compose up -d

# Verificar status
docker-compose ps

# Ver logs
docker-compose logs -f app
docker-compose logs -f nginx
```

### 4. Verificar disponibilidade

```bash
# HTTP local
curl http://localhost:8000

# Via Nginx
curl http://localhost:80
```

## Comandos Úteis com Docker

### Gerenciamento de Containers

```bash
# Ver status
docker-compose ps

# Ver logs da app
docker-compose logs -f app

# Ver logs do Nginx
docker-compose logs -f nginx

# Acessar container
docker-compose exec app bash

# Reiniciar serviço
docker-compose restart app
docker-compose restart nginx

# Parar e iniciar
docker-compose stop
docker-compose start

# Remover containers (sem perder dados)
docker-compose down

# Remover tudo (incluindo volumes)
docker-compose down -v
```

### Executar Comandos

```bash
# Dentro do container
docker-compose exec app python -c "import web_app; print('OK')"

# Ver banco de dados
docker-compose exec app sqlite3 instance/rastreamentos.db ".tables"

# Atualizar código
docker-compose exec app pip install -r requirements.txt
docker-compose restart app
```

## 🏗️ Arquitetura com Docker

```
┌─────────────────────────────────────┐
│  Cliente (Navegador)                │
└────────────┬────────────────────────┘
             │
             │ TCP 80, 443 (HTTPS)
             │
  ┌──────────▼──────────────────────────────────┐
  │                                             │
  │  Docker Container: Nginx                   │
  │  - Proxy reverso                           │
  │  - SSL/TLS                                 │
  │  - Port 80, 443 expostas                   │
  │                                             │
  └──────────┬──────────────────────────────────┘
             │
             │ Docker Network (interno)
             │ kairos-rastreio_kairos-network
             │
  ┌──────────▼──────────────────────────────────┐
  │                                             │
  │  Docker Container: Flask App               │
  │  - Gunicorn (4 workers)                    │
  │  - Port 8000 (interno)                     │
  │  - Flask Application                       │
  │                                             │
  └──────────┬──────────────────────────────────┘
             │
             ├─────────────────────┐
             │                     │
             ▼                     ▼
         Database            API Externa
       (SQLite)            (SiteRastreio)
       Volume persistente
```

## 🔒 Segurança com Docker

### 1. Variáveis de Ambiente

```bash
# Arquivo .env (não versionado no Git)
SITERASTREIO_TOKEN=seu_token
FLASK_ENV=production

# Adicionar ao .gitignore
echo ".env" >> .gitignore
```

### 2. Permissões

```bash
# .env é acessível apenas pelo usuário
chmod 600 .env

# Diretórios com permissões apropriadas
chmod 755 logs/
chmod 755 instance/
```

### 3. Imagem Segura

O Dockerfile usa:
- Python slim image (menor attack surface)
- Usuário não-root (appuser)
- Health checks automáticos
- UID 1000 para isolamento

## 📊 Monitoramento

### Logs em tempo real

```bash
# App
docker-compose logs -f app

# Nginx
docker-compose logs -f nginx

# Todos
docker-compose logs -f
```

### Estatísticas

```bash
# Uso de recursos
docker stats kairos-rastreio-app kairos-rastreio-nginx

# Inspecionar container
docker container inspect kairos-rastreio-app
```

### Health Check

```bash
# Verificar saúde
docker-compose ps

# Ver detalhes do health check
docker inspect --format='{{json .State.Health}}' kairos-rastreio-app | jq
```

## 🔄 Updates e Manutenção

### Atualizar código

```bash
# Pull da latest versão
git pull

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose up -d
```

### Atualizar dependências Python

```bash
# Editar requirements.txt
nano requirements.txt

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose restart app
```

### Backup

```bash
# Backup do banco de dados
docker-compose exec app cp instance/rastreamentos.db instance/rastreamentos.db.backup

# Ou copiar do volume
docker cp kairos-rastreio-app:/app/instance ./backup_$(date +%Y%m%d)
```

## 🌐 Configuração com Nginx e SSL

### Usar certificado Let's Encrypt

```bash
# 1. Obter certificado (antes de usar container)
sudo certbot certonly --standalone -d seu_dominio.com

# 2. Copiar certificados
mkdir -p certs
sudo cp /etc/letsencrypt/live/seu_dominio.com/fullchain.pem certs/
sudo cp /etc/letsencrypt/live/seu_dominio.com/privkey.pem certs/
sudo chown $USER:$USER certs/*

# 3. Atualizar nginx.conf com paths dos certs
# 4. Iniciar containers
docker-compose up -d
```

### Renovação automática de SSL

```bash
# Criar script de renovação
cat > renew-ssl.sh << 'EOF'
#!/bin/bash
certbot renew --quiet
docker-compose exec nginx nginx -s reload
EOF

chmod +x renew-ssl.sh

# Adicionar ao crontab (diariamente)
crontab -e
# Adicionar: 0 12 * * * /home/seu-usuario/kairos-rastreio/renew-ssl.sh
```

## 🆚 Comparação: Docker vs Deployment Manual

| Aspecto | Docker | Manual |
|---------|--------|--------|
| Setup | Mais rápido | Mais lento |
| Isolamento | Melhor | Depende de configs |
| Portabilidade | Excelente | Dependente do servidor |
| Backup | Mais fácil | Precisa scripts |
| Updates | Simples | Mais passos |
| Performance | Ligeiramente menor | Melhor |
| Custo Resources | Um pouco mais | Menos overhead |

## 📱 Deploy em Múltiplas Máquinas

Com Docker, é muito fácil replicar em outro servidor:

```bash
# Novo servidor
git clone seu-repositorio
cd kairos-rastreio
nano .env  # Configurar variáveis
docker-compose up -d
```

## 🆘 Troubleshooting Docker

### Container não inicia

```bash
# Ver logs
docker-compose logs app

# Rebuild
docker-compose build --no-cache

# Remover e recriar
docker-compose down
docker-compose up -d
```

### Port já em uso

```bash
# Ver qual processo usa a porta
lsof -i :80
lsof -i :443
lsof -i :8000

# Matar processo conflitante
kill -9 <PID>
```

### Banco de dados corrompido

```bash
# Backup
docker cp kairos-rastreio-app:/app/instance/rastreamentos.db ./backup.db

# Remover volume (cuidado!)
docker-compose down -v

# Recriar
docker-compose up -d
```

## 📚 Referências

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Python Image](https://hub.docker.com/_/python)
- [Nginx Image](https://hub.docker.com/_/nginx)

---

**Próximo passo**: Escolher entre Docker ou deployment manual, seguindo o guia correspondente em `DEPLOYMENT.md` ou `QUICK-START.md`.
