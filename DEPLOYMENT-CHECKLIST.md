# Checklist de Deployment - Kairos Rastreio

## 📋 Guia de Acompanhamento

Use este checklist durante seu deployment para garantir que todos os passos foram realizados.

---

## 🚀 OPTION A: Deployment Automático (Recomendado)

### Setup Local
- [ ] Repositório clonado ou arquivos prontos
- [ ] Arquivo `deploy.sh` presente
- [ ] Arquivo `requirements.txt` configurado
- [ ] Arquivo `.env` criado (opcional, será criado pelo script)

### No Servidor Ubuntu 22.04

```bash
sudo su                    # Entrar como root
bash deploy.sh            # Executar script automático
```

- [ ] Sistema atualizado
- [ ] Dependências instaladas (Python, Nginx, etc)
- [ ] Virtual environment criado
- [ ] Dependências Python instaladas
- [ ] Arquivo .env criado
- [ ] Serviço systemd instalado
- [ ] Nginx configurado
- [ ] Permissões ajustadas

### Pós-Deploy Automático

```bash
# Configurar domínio
sudo nano /etc/nginx/sites-available/kairos-rastreio
# Substituir: seu_dominio.com → seu_dominio_real.com

# Configurar variáveis
sudo nano /var/www/kairos-rastreio/.env
# Adicionar: SITERASTREIO_TOKEN=seu_token

# Obter SSL
sudo certbot --nginx -d seu_dominio.com

# Iniciar
sudo systemctl start kairos-rastreio.service
sudo systemctl restart nginx

# Verificar
sudo systemctl status kairos-rastreio.service
curl -I https://seu_dominio.com
```

---

## 🐳 OPTION B: Deployment com Docker

### Local
- [ ] Docker instalado
- [ ] Docker Compose instalado
- [ ] `Dockerfile` presente
- [ ] `docker-compose.yml` presente
- [ ] `.env` criado e preenchido

### Servidor

```bash
# Instalar Docker e Docker Compose
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
sudo apt install docker-compose -y

# Clone/copie arquivo
git clone seu-repositorio
cd kairos-rastreio

# Configurar variáveis
nano .env
# SITERASTREIO_TOKEN=seu_token
chmod 600 .env

# Build e deploy
docker-compose build
docker-compose up -d

# Verificar
docker-compose ps
docker-compose logs -f app
```

---

## 🔧 Pós-Deployment - Ambas as Opções

### Verificação Funcional

- [ ] Aplicação responde em `http://localhost:8000` (SSH tunnel)
- [ ] Nginx responde em `http://seu_dominio.com`
- [ ] Redirecionamento HTTPS funciona
- [ ] SSL valido (não há warnings)
- [ ] Arquivo `.env` está protegido (chmod 600)
- [ ] Banco de dados criado
- [ ] Arquivos estáticos servidos corretamente
- [ ] Serviço reinicia automaticamente no boot

### Testes de API

```bash
# Testar rastreamento (ssh tunnel necessário)
curl -X POST http://localhost:8000/api/rastreamento \
  -H "Content-Type: application/json" \
  -d '{"codigo": "AN619556349BR"}'

# Verificar resposta
# Deve retornar JSON com dados de rastreamento
```

### Checklist de Segurança

- [ ] SSL/TLS ativo (HTTPS)
- [ ] `.env` não está em Git (`.gitignore`)
- [ ] `.env` tem permissão 600
- [ ] Gunicorn roda em 127.0.0.1:8000 (não acessível externamente)
- [ ] Nginx é proxy reverso configurado
- [ ] Firewall permite 80, 443 (e 22 para SSH)
- [ ] Certificado SSL válido (Let's Encrypt / Certbot)
- [ ] Headers de segurança no Nginx (HSTS, CSP, etc)
- [ ] Logs são acessíveis
- [ ] Backups configurados

---

## 📊 Monitoramento Contínuo

### Logs
```bash
# Aplicação
journalctl -u kairos-rastreio.service -f

# Nginx
tail -f /var/log/nginx/kairos-rastreio-error.log

# Sistema
tail -f /var/log/syslog

# Docker (se usar Docker)
docker-compose logs -f
```

- [ ] Logs configurados e acessíveis
- [ ] Sem erros críticos nos logs
- [ ] Rotação de logs configurada

### Health Check
```bash
# Verificar saúde
curl -I https://seu_dominio.com/

# Status esperado: 200 OK
```

- [ ] Aplicação responde com código 200
- [ ] Tempo de resposta aceitável (< 500ms)
- [ ] Sem erros 5xx

### Performance
```bash
# Monitorar recursos
top -u www-data        # Para deployment manual
docker stats            # Para Docker

# Ver conexões
netstat -tan | grep :8000 | wc -l
```

- [ ] Uso de memória OK (< 500MB)
- [ ] CPU não constantemente alta
- [ ] Sem conexões penduradas

---

## 🔄 Atualização de Código

### Quando atualizar:

```bash
# Deployment Manual
cd /var/www/kairos-rastreio
sudo git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart kairos-rastreio.service

# Docker
cd caminho/do/projeto
git pull
docker-compose build --no-cache
docker-compose up -d
```

- [ ] Código atualizado do repositório
- [ ] Novas dependências instaladas
- [ ] Testes executados
- [ ] Serviço reiniciado
- [ ] Funcionalidades verificadas

---

## 🆘 Troubleshooting Quick

| Problema | Comando |
|----------|---------|
| Aplicação não inicia | `sudo journalctl -u kairos-rastreio.service -n 50` |
| 502 Bad Gateway | `sudo systemctl restart kairos-rastreio.service` |
| Erro de conectividade | `curl http://127.0.0.1:8000` |
| Erro de permissão | `sudo chown -R www-data:www-data /var/www/kairos-rastreio` |
| SSL não funciona | `sudo certbot --nginx -d seu_dominio.com` |
| Porta em uso | `sudo lsof -i :8000` |

---

## 📋 Informações Críticas

### Variáveis de Ambiente
```
SITERASTREIO_TOKEN = ______________________
FLASK_ENV = production
DOMINIO = seu_dominio.com
```

### Caminhos Importantes
```
Raiz da aplicação:    /var/www/kairos-rastreio
Banco de dados:       /var/www/kairos-rastreio/instance/rastreamentos.db
Logs:                 /var/log/kairos-rastreio/
Nginx config:         /etc/nginx/sites-available/kairos-rastreio
Systemd config:       /etc/systemd/system/kairos-rastreio.service
```

### Comandos Frequentes
```bash
# Status
sudo systemctl status kairos-rastreio.service

# Logs
sudo journalctl -u kairos-rastreio.service -f

# Reiniciar
sudo systemctl restart kairos-rastreio.service

# Parar
sudo systemctl stop kairos-rastreio.service

# Iniciar
sudo systemctl start kairos-rastreio.service
```

---

## ✅ Checklist Final

- [ ] Aplicação online e respondendo
- [ ] SSL válido e automático
- [ ] Banco de dados criado e acessível
- [ ] Variáveis de ambiente configuradas
- [ ] Logs configurados e monitoráveis
- [ ] Backups agendados
- [ ] Firewall configurado
- [ ] Monitoramento ativo
- [ ] Documentação atualizada
- [ ] Time informado sobre deployment

---

## 📞 Próximos Passos

1. **Documentação**: Ler `DEPLOYMENT.md` completo
2. **Segurança**: Revisar `SECURITY.md`
3. **Arquitetura**: Entender `ARCHITECTURE.md`
4. **Monitoramento**: Configurar alerts e backups
5. **Testes**: Testar cenários de falha
6. **Manutenção**: Agendar reviews mensais da saúde da aplicação

---

**Data de Deploy**: ________________
**Responsável**: ________________
**Notas**: 
```
_________________________________
_________________________________
_________________________________
```

**Versão do checklist**: v1.0 (Março/2026)
