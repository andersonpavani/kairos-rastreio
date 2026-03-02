#!/bin/bash

# Script de instalação automática - Kairos Rastreio
# Uso: sudo bash deploy.sh

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se é root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script deve ser executado como root (use 'sudo bash deploy.sh')"
   exit 1
fi

print_info "Iniciando deploy do Kairos Rastreio..."

# 1. Atualizar sistema
print_info "Atualizando sistema..."
apt update && apt upgrade -y

# 2. Instalar dependências
print_info "Instalando dependências..."
apt install -y python3 python3-pip python3-venv git nginx curl supervisor

# 3. Criar diretório da aplicação
print_info "Criando diretório da aplicação..."
mkdir -p /var/www/kairos-rastreio
mkdir -p /var/log/kairos-rastreio

# 4. Clonar repositório (ajuste conforme necessário)
if [ ! -d "/var/www/kairos-rastreio/.git" ]; then
    print_info "Clonando repositório..."
    # AJUSTE ESTE COMANDO COM SEU REPOSITÓRIO
    # git clone <seu-repositorio> /var/www/kairos-rastreio
    print_warning "Por favor, copie seus arquivos para /var/www/kairos-rastreio"
else
    print_info "Repositório já existe, atualizando..."
    cd /var/www/kairos-rastreio
    git pull
fi

# 5. Criar virtual environment
print_info "Criando virtual environment..."
cd /var/www/kairos-rastreio
python3 -m venv venv

# 6. Ativar venv e instalar dependências
print_info "Instalando dependências Python..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install gunicorn

# 7. Criar arquivo .env
if [ ! -f "/var/www/kairos-rastreio/.env" ]; then
    print_info "Criando arquivo .env..."
    cat > /var/www/kairos-rastreio/.env << EOF
# Variáveis de ambiente
SITERASTREIO_TOKEN=seu_token_aqui
FLASK_ENV=production
EOF
    chmod 600 /var/www/kairos-rastreio/.env
    print_warning "ATENÇÃO: Configure o arquivo .env com seus dados:"
    print_warning "  - SITERASTREIO_TOKEN=seu_token_aqui"
fi

# 8. Configurar permissões
print_info "Configurando permissões..."
chown -R www-data:www-data /var/www/kairos-rastreio
chmod -R 755 /var/www/kairos-rastreio
chmod 600 /var/www/kairos-rastreio/.env
chmod 755 /var/log/kairos-rastreio

# 9. Instalar arquivo de serviço
print_info "Instalando serviço systemd..."
cp /var/www/kairos-rastreio/kairos-rastreio.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable kairos-rastreio.service

# 10. Configurar Nginx
print_info "Configurando Nginx..."
cp /var/www/kairos-rastreio/nginx-config.conf /etc/nginx/sites-available/kairos-rastreio

# Desabilitar site padrão
if [ -f "/etc/nginx/sites-enabled/default" ]; then
    rm /etc/nginx/sites-enabled/default
fi

# Habilitar novo site
ln -sf /etc/nginx/sites-available/kairos-rastreio /etc/nginx/sites-enabled/

# Testar configuração
if ! nginx -t; then
    print_error "Erro na configuração do Nginx. Verifique o arquivo nginx-config.conf"
    exit 1
fi

# 11. Instalar e configurar SSL (opcional)
print_info "Instalando certbot para SSL..."
apt install -y certbot python3-certbot-nginx

# Exibir instruções finais
echo ""
echo "======================================"
echo -e "${GREEN}Deploy concluído com sucesso!${NC}"
echo "======================================"
echo ""
echo "Próximas etapas:"
echo ""
echo "1. ${YELLOW}Configurar DOMÍNIO e SSL${NC}:"
echo "   - Edite /etc/nginx/sites-available/kairos-rastreio"
echo "   - Substitua 'seu_dominio.com' pelo seu domínio"
echo "   - Rode: sudo certbot --nginx -d seu_dominio.com"
echo ""
echo "2. ${YELLOW}Configurar variáveis de ambiente${NC}:"
echo "   - sudo nano /var/www/kairos-rastreio/.env"
echo "   - Adicione seu SITERASTREIO_TOKEN"
echo ""
echo "3. ${YELLOW}Iniciar o serviço${NC}:"
echo "   - sudo systemctl start kairos-rastreio.service"
echo "   - sudo systemctl status kairos-rastreio.service"
echo ""
echo "4. ${YELLOW}Reiniciar Nginx${NC}:"
echo "   - sudo systemctl restart nginx"
echo ""
echo "5. ${YELLOW}Ver logs${NC}:"
echo "   - sudo journalctl -u kairos-rastreio.service -f"
echo "   - sudo tail -f /var/log/nginx/kairos-rastreio-error.log"
echo ""
echo "======================================"
