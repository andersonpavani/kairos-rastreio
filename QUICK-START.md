# Guia Rápido de Deploy - Kairos Rastreio

## Instalação Automática (RECOMENDADO)

```bash
# 1. No servidor Ubuntu 22.04, como root:
sudo bash deploy.sh

# Siga as instruções na tela
```

## Instalação Manual (Passo a Passo)

### 1️⃣ Preparar o servidor

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx
```

### 2️⃣ Clonar/copiar a aplicação

```bash
sudo mkdir -p /var/www/kairos-rastreio
cd /var/www/kairos-rastreio

# Se tem git:
# sudo git clone <seu-repositorio> .

# Ou copie os arquivos manualmente
```

### 3️⃣ Instalar dependências Python

```bash
sudo python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 4️⃣ Criar arquivo .env

```bash
sudo nano /var/www/kairos-rastreio/.env
```

Adicione:
```
SITERASTREIO_TOKEN=seu_token_aqui
FLASK_ENV=production
```

### 5️⃣ Instalar como serviço systemd

```bash
# Copiar arquivo de serviço
sudo cp kairos-rastreio.service /etc/systemd/system/

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar no boot
sudo systemctl enable kairos-rastreio.service

# Iniciar
sudo systemctl start kairos-rastreio.service

# Verificar status
sudo systemctl status kairos-rastreio.service
```

### 6️⃣ Configurar Nginx

```bash
# Copiar configuração
sudo cp nginx-config.conf /etc/nginx/sites-available/kairos-rastreio

# Ou editar manualmente
sudo nano /etc/nginx/sites-available/kairos-rastreio

# Edite e substitua "seu_dominio.com" pelo seu domínio, depois:
sudo ln -s /etc/nginx/sites-available/kairos-rastreio /etc/nginx/sites-enabled/

# Desabilitar site padrão
sudo rm /etc/nginx/sites-enabled/default

# Testar
sudo nginx -t

# Reiniciar
sudo systemctl restart nginx
```

### 7️⃣ Configurar SSL (Let's Encrypt)

```bash
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu_dominio.com

# Verificar renovação automática
sudo systemctl status certbot.timer
```

### 8️⃣ Configurar permissões

```bash
sudo chown -R www-data:www-data /var/www/kairos-rastreio
sudo chmod -R 755 /var/www/kairos-rastreio
sudo chmod 600 /var/www/kairos-rastreio/.env
```

## Comandos Essenciais

### Status da aplicação
```bash
sudo systemctl status kairos-rastreio.service
```

### Ver logs em tempo real
```bash
sudo journalctl -u kairos-rastreio.service -f
```

### Reiniciar aplicação
```bash
sudo systemctl restart kairos-rastreio.service
```

### Parar aplicação
```bash
sudo systemctl stop kairos-rastreio.service
```

### Ver erros do Nginx
```bash
sudo tail -f /var/log/nginx/kairos-rastreio-error.log
```

### Atualizar código

```bash
cd /var/www/kairos-rastreio

# Puxar última versão
sudo git pull

# Instalar novas dependências se houver
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar
sudo systemctl restart kairos-rastreio.service
```

## Verificar se está funcionando

```bash
# Acessar via curl (se em HTTP)
curl http://localhost:8000

# Ou acessar via navegador
# http://seu_dominio.com
# https://seu_dominio.com (depois de SSL)
```

## Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| `Permission denied` | `sudo chown -R www-data:www-data /var/www/kairos-rastreio` |
| Porta 8000 já em uso | `sudo lsof -i :8000` e depois `sudo kill -9 <PID>` |
| Erro no Nginx | `sudo nginx -t` e ver logs em `/var/log/nginx/error.log` |
| Aplicação não inicia | `sudo journalctl -u kairos-rastreio.service -n 50` |
| Assets estáticos não carregam | Verificar se `/var/www/kairos-rastreio/static/` existe |

## Monitoramento Contínuo

Para monitorar a saúde da aplicação:

```bash
# Ver uso de memória
top -u www-data

# Verificar se serviço está rodando
watch -n 2 'systemctl status kairos-rastreio.service'

# Contar conexões
netstat -an | grep 8000 | wc -l
```
