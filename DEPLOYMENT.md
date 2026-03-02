# Guia de Deployment - Kairos Rastreio

## Pré-requisitos
- Ubuntu 22.04
- Acesso root ou sudo
- Domínio configurado (opcional)

## Passo 1: Preparar o servidor Ubuntu

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências essenciais
sudo apt install -y python3 python3-pip python3-venv git nginx curl

# Verificar versão do Python
python3 --version
```

## Passo 2: Preparar o diretório da aplicação

```bash
# Criar diretório para a aplicação
sudo mkdir -p /var/www/kairos-rastreio
cd /var/www/kairos-rastreio

# Clonar o repositório (ou copiar os arquivos)
sudo git clone <seu-repositorio> .

# Criar virtual environment
sudo python3 -m venv venv

# Ativar virtual environment
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

## Passo 3: Criar arquivo .env

```bash
# Criar arquivo .env com suas variáveis de ambiente
sudo nano /var/www/kairos-rastreio/.env
```

Conteúdo do .env:
```
SITERASTREIO_TOKEN=seu_token_aqui
FLASK_ENV=production
```

## Passo 4: Criar arquivo de serviço systemd

```bash
sudo nano /etc/systemd/system/kairos-rastreio.service
```

Conteúdo do arquivo (veja arquivo `kairos-rastreio.service` deste projeto).

## Passo 5: Habilitar e iniciar o serviço

```bash
# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço para iniciar no boot
sudo systemctl enable kairos-rastreio.service

# Iniciar o serviço
sudo systemctl start kairos-rastreio.service

# Verificar status
sudo systemctl status kairos-rastreio.service

# Ver logs
sudo journalctl -u kairos-rastreio.service -f
```

## Passo 6: Configurar Nginx como proxy reverso

```bash
# Criar arquivo de configuração
sudo nano /etc/nginx/sites-available/kairos-rastreio
```

Conteúdo do arquivo (veja arquivo `nginx-config.conf` deste projeto).

```bash
# Habilitar site
sudo ln -s /etc/nginx/sites-available/kairos-rastreio /etc/nginx/sites-enabled/

# Desabilitar site padrão se necessário
sudo rm /etc/nginx/sites-enabled/default

# Verificar configuração
sudo nginx -t

# Reiniciar Nginx
sudo systemctl restart nginx
```

## Passo 7: Configurar SSL/TLS com Let's Encrypt (recomendado)

```bash
# Instalar certbot
sudo apt install -y certbot python3-certbot-nginx

# Obter certificado (substitua seu_dominio.com pelo seu domínio)
sudo certbot --nginx -d seu_dominio.com

# Renovação automática (já vem configurada)
sudo systemctl status certbot.timer
```

## Passo 8: Configurar permissões

```bash
# Definir proprietário
sudo chown -R www-data:www-data /var/www/kairos-rastreio

# Definir permissões corretas
sudo chmod -R 755 /var/www/kairos-rastreio
sudo chmod 600 /var/www/kairos-rastreio/.env
```

## Monitoramento e Manutenção

### Ver status do serviço
```bash
sudo systemctl status kairos-rastreio.service
```

### Ver logs em tempo real
```bash
sudo journalctl -u kairos-rastreio.service -f
```

### Reiniciar serviço
```bash
sudo systemctl restart kairos-rastreio.service
```

### Parar serviço
```bash
sudo systemctl stop kairos-rastreio.service
```

### Atualizar aplicação
```bash
cd /var/www/kairos-rastreio
sudo git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kairos-rastreio.service
```

## Troubleshooting

### Verificar se porta 8000 está em uso
```bash
sudo lsof -i :8000
```

### Verificar erros do Nginx
```bash
sudo tail -f /var/log/nginx/error.log
```

### Verificar erros da aplicação
```bash
sudo journalctl -u kairos-rastreio.service -n 50
```

### Recarregar configuração do Nginx
```bash
sudo systemctl reload nginx
```

## Estrutura final esperada

```
/var/www/kairos-rastreio/
├── venv/                    # Virtual environment
├── app.py
├── models.py
├── web_app.py
├── requirements.txt
├── .env                     # Variáveis de ambiente
├── static/
├── templates/
└── instance/
```
