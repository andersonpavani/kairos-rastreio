# Segurança e Otimização - Kairos Rastreio

## ✅ Checklist Pré-Deploy

Antes de colocar em produção, verifique:

- [ ] Arquivo `.env` está configurado corretamente
- [ ] SITERASTREIO_TOKEN está preenchido
- [ ] Banco de dados (SQLite) está em `/var/www/kairos-rastreio/instance/`
- [ ] Diretório `/var/log/kairos-rastreio/` foi criado
- [ ] Arquivo `nginx-config.conf` usa seu domínio
- [ ] SSL/TLS está configurado (certbot)
- [ ] Permissões de arquivo estão corretas (755 para diretorios, 600 para .env)
- [ ] Firewall permite portas 80 e 443
- [ ] Backups estão configurados

## 🔒 Recomendações de Segurança

### 1. Variáveis de Ambiente
```bash
# Nunca commitar .env no Git
echo ".env" >> /var/www/kairos-rastreio/.gitignore

# Proteger arquivo .env
sudo chmod 600 /var/www/kairos-rastreio/.env
```

### 2. Firewall (UFW)
```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar regras
sudo ufw status
```

### 3. Fail2Ban (proteção contra brute force)
```bash
# Instalar
sudo apt install -y fail2ban

# Criar configuração
sudo nano /etc/fail2ban/jail.local

# Adicionar:
# [DEFAULT]
# bantime = 3600
# findtime = 600
# maxretry = 5
#
# [sshd]
# enabled = true
# [recidive]
# enabled = true

sudo systemctl restart fail2ban
```

### 4. Limpar dados sensíveis
```bash
# Remover cache Python
find /var/www/kairos-rastreio -type d -name __pycache__ -exec rm -rf {} +

# Remover arquivos .pyc
find /var/www/kairos-rastreio -type f -name "*.pyc" -delete
```

### 5. Melhorar Gunicorn
```bash
# Usar mais workers (2 x núcleos de CPU + 1)
# Para 4 cores: 9 workers
# Editar /etc/systemd/system/kairos-rastreio.service
# ExecStart=/var/www/kairos-rastreio/venv/bin/gunicorn \
#     --workers 9 \
#     --worker-class sync \
#     --bind 127.0.0.1:8000 \
```

### 6. HTTPS/SSL Obrigatório
```bash
# A configuração nginx-config.conf já faz isso
# Redireciona HTTP para HTTPS automaticamente
```

### 7. Headers de Segurança
```bash
# Já incluído em nginx-config.conf:
# - Strict-Transport-Security
# - X-Content-Type-Options
# - X-Frame-Options
```

### 8. Gzip Compression
```bash
# Já habilitado em nginx-config.conf
# Reduz tamanho da transferência
```

## 📊 Monitoramento

### Instalar Monit (opcional)
```bash
sudo apt install -y monit

# Criar config
sudo nano /etc/monit/monitrc

# Adicionar monitoramento do serviço:
# check process kairos-rastreio with pidfile /var/run/kairos-rastreio.pid
#     start program = "/bin/systemctl start kairos-rastreio.service"
#     stop program = "/bin/systemctl stop kairos-rastreio.service"
#     if failed port 8000 then restart

sudo monit start
```

### Scripts de Monitoramento

```bash
#!/bin/bash
# Salvar como: /usr/local/bin/check-kairos.sh

# Verificar se serviço está rodando
systemctl is-active --quiet kairos-rastreio.service || {
    echo "ERRO: Serviço kairos-rastreio não está rodando!"
    systemctl restart kairos-rastreio.service
}

# Verificar disco
df -h /var/www/kairos-rastreio | tail -1 | awk '{print $5}' | sed 's/%//' | {
    read usage
    if [ "$usage" -gt 80 ]; then
        echo "AVISO: Uso de disco em /var/www/kairos-rastreio: ${usage}%"
    fi
}

# Verificar se Nginx está respondendo
curl -s -o /dev/null -w "%{http_code}" https://seu_dominio.com | grep -q "200" || {
    echo "ERRO: Nginx não está respondendo corretamente"
    systemctl restart nginx
}
```

Adicionar ao crontab:
```bash
sudo crontab -e
# Adicionar: */5 * * * * /usr/local/bin/check-kairos.sh
```

## 🔄 Backup

### Backup Automático
```bash
#!/bin/bash
# Salvar como: /usr/local/bin/backup-kairos.sh

BACKUP_DIR="/home/backups/kairos-rastreio"
mkdir -p "$BACKUP_DIR"

# Data
DATE=$(date +%Y%m%d_%H%M%S)

# Fazer backup do banco de dados
sudo cp -r /var/www/kairos-rastreio/instance "$BACKUP_DIR/instance_$DATE"

# Comprimir
tar -czf "$BACKUP_DIR/kairos-backup_$DATE.tar.gz" \
    /var/www/kairos-rastreio/instance \
    /var/www/kairos-rastreio/.env

# Remover backups antigos (manter últimos 30 dias)
find "$BACKUP_DIR" -name "kairos-backup_*.tar.gz" -mtime +30 -delete

echo "Backup criado: $BACKUP_DIR/kairos-backup_$DATE.tar.gz"
```

No crontab (diariamente às 2 AM):
```bash
0 2 * * * /usr/local/bin/backup-kairos.sh
```

## 📈 Otimização

### Aumentar limites do sistema
```bash
# Editar /etc/security/limits.conf
sudo nano /etc/security/limits.conf

# Adicionar:
# www-data soft nofile 65535
# www-data hard nofile 65535
# www-data soft nproc 65535
# www-data hard nproc 65535
```

### Cache do Nginx
```bash
# Já incluído em nginx-config.conf
# expires 30d para arquivos estáticos
```

### Ajustar pool de conexões Gunicorn
```bash
# Se aplicação usa muita memória:
# Reduzir workers em /etc/systemd/system/kairos-rastreio.service
# --workers 2 (mínimo)
```

### Database Connection Pool
Adicionar em `web_app.py` se necessário:
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
```

## 🔍 Logs Importantes

```bash
# Aplicação
sudo journalctl -u kairos-rastreio.service -f

# Nginx - Acesso
sudo tail -f /var/log/nginx/kairos-rastreio-access.log

# Nginx - Erro
sudo tail -f /var/log/nginx/kairos-rastreio-error.log

# Sistema
sudo tail -f /var/log/syslog
```

## 📞 Suporte e Debug

```bash
# Testar conectividade com API externa
curl -H "Authorization: Bearer $TOKEN" \
     https://seurastreio.com.br/api/public/rastreio/AN619556349BR

# Testar conexão Nginx <-> Gunicorn
sudo curl -H "Host: seu_dominio.com" http://127.0.0.1:8000

# Status de porta
sudo netstat -tlnp | grep 8000
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```
