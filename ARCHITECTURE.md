# 🚀 Kairos Rastreio - Guia de Deployment

Uma aplicação Flask para rastreamento de encomendas com deploy em Ubuntu 22.04 como serviço systemd.

## 📋 Arquivos de Deploy Inclusos

| Arquivo | Descrição |
|---------|-----------|
| `deploy.sh` | Script automático de instalação completa |
| `kairos-rastreio.service` | Arquivo de configuração systemd |
| `nginx-config.conf` | Configuração do Nginx como proxy reverso |
| `DEPLOYMENT.md` | Guia detalhado com todos os passos |
| `QUICK-START.md` | Guia rápido de referência |
| `SECURITY.md` | Recomendações e checklist de segurança |
| `ARCHITECTURE.md` | Diagrama e explicação da arquitetura |

## ⚡ Instalação Rápida (30 minutos)

### 1. No seu computador local:

```bash
# Clone o repositório (ou tenha os arquivos prontos)
git clone <seu-repositorio>
cd kairos-rastreio
```

### 2. No servidor Ubuntu 22.04 (como root):

```bash
# Entre como root
sudo su

# Upload dos arquivos (ou git clone)
# ...

# Execute o script automático
bash deploy.sh
```

### 3. Configurações finais no servidor:

```bash
# Editar domínio e SSL
sudo nano /etc/nginx/sites-available/kairos-rastreio
# Substitua: seu_dominio.com pelo seu domínio

# Obter SSL
sudo certbot --nginx -d seu_dominio.com

# Configurar variáveis de ambiente
sudo nano /var/www/kairos-rastreio/.env
# Adicione: SITERASTREIO_TOKEN=seu_token

# Iniciar serviço
sudo systemctl start kairos-rastreio.service
sudo systemctl restart nginx
```

Pronto! 🎉

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Cliente (Navegador)                                │
│                                                     │
└────────────────────┬────────────────────────────────┘
                     │
                     │ HTTPS (443)
                     │
        ┌────────────▼────────────┐
        │                         │
        │   Nginx (Proxy Reverso) │◄─── HTTP (80) → HTTPS
        │                         │
        │ - SSL/TLS              │
        │ - Compressão Gzip      │
        │ - Cache estático       │
        │ - Rate limiting        │
        │                         │
        └────────────┬────────────┘
                     │
                     │ HTTP (127.0.0.1:8000)
                     │
        ┌────────────▼────────────────────┐
        │                                 │
        │  Gunicorn (WSGI Application    │
        │  Server)                        │
        │                                 │
        │ - 4 workers                     │
        │ - Gerencia requisições          │
        │ - Rota para Flask               │
        │                                 │
        └────────────┬────────────────────┘
                     │
                     │
        ┌────────────▼────────────────────┐
        │                                 │
        │  Flask Application              │
        │  (web_app.py)                   │
        │                                 │
        │ - Rotas HTTP                    │
        │ - Templates HTML                │
        │ - Lógica de negócio             │
        │                                 │
        └────────────┬────────────────────┘
                     │
        ┌────────────┴─────────────────────┐
        │                                  │
        │ SQLAlchemy ORM                   │ API Externa
        │                                  │
        ▼                                  ▼
    ┌────────────┐           ┌──────────────────────┐
    │            │           │                      │
    │  SQLite    │           │  SiteRastreio API    │
    │ (Banco de  │           │  (seurastreio.com)   │
    │   dados)   │           │                      │
    │            │           │  - Rastreamento      │
    └────────────┘           │  - Tracking info     │
                             │                      │
                             └──────────────────────┘
```

## 🔄 Fluxo de Requisição

1. **Cliente** faz requisição HTTPS → Nginx (porta 443)
2. **Nginx** comprime resposta, valida SSL, faz proxy → Gunicorn (127.0.0.1:8000)
3. **Gunicorn** processa requisição → Flask application
4. **Flask** executa lógica:
   - Se precisa dados: consulta API externa (SiteRastreio)
   - Salva dados no SQLite (banco de dados local)
   - Renderiza template HTML
5. **Resposta** volta: Flask → Gunicorn → Nginx → Cliente (HTTPS)

## 📊 Componentes do Sistema

### Nginx
- **Porta**: 80 (HTTP) e 443 (HTTPS)
- **Função**: Proxy reverso, SSL/TLS, compressão
- **Config**: `/etc/nginx/sites-available/kairos-rastreio`

### Gunicorn
- **Porta**: 127.0.0.1:8000 (localhost apenas)
- **Função**: Servidor de aplicação WSGI
- **Workers**: 4 (ajustável conforme CPU)
- **Config**: `/etc/systemd/system/kairos-rastreio.service`

### Flask + SQLAlchemy
- **Arquivo**: `/var/www/kairos-rastreio/web_app.py`
- **Banco de dados**: SQLite (`/var/www/kairos-rastreio/instance/rastreamentos.db`)
- **Função**: Lógica da aplicação, rotas HTTP

### Systemd
- **Serviço**: `kairos-rastreio.service`
- **Usuário**: `www-data`
- **Auto-restart**: Sim
- **Logs**: `journalctl -u kairos-rastreio.service`

## 📁 Estrutura de Diretórios

```
/var/www/kairos-rastreio/        # Raiz da aplicação
├── venv/                         # Virtual environment Python
├── static/                       # Arquivos estáticos (CSS, JS, imagens)
├── templates/                    # Templates HTML
├── instance/                     # Banco de dados SQLite
├── web_app.py                    # Aplicação Flask principal
├── models.py                     # Modelos SQLAlchemy
├── .env                          # Variáveis de ambiente (privado)
├── requirements.txt              # Dependências Python
└── README.md                     # Documentação

/var/log/kairos-rastreio/         # Logs da aplicação
├── access.log                    # Logs de acesso (Nginx)
└── error.log                     # Logs de erro (Gunicorn + Nginx)

/etc/systemd/system/
└── kairos-rastreio.service       # Configuração do serviço

/etc/nginx/
├── sites-available/
│   └── kairos-rastreio           # Configuração Nginx
└── sites-enabled/
    └── kairos-rastreio -> ../sites-available/kairos-rastreio
```

## 🛡️ Segurança

### SSL/TLS (HTTPS)
- Certificado automático via Let's Encrypt
- Renovação automática com certbot
- Redirecionamento HTTPS obrigatório

### Isolamento
- Gunicorn roda em `127.0.0.1:8000` (não acessível externamente)
- Nginx é o único ponto de entrada externo
- Arquivos protegidos com permissões adequadas

### Variáveis de Ambiente
- Tokens sensíveis em `.env` (não versionado)
- Arquivo `.env` com permissões 600 (apenas leitura pelo usuário www-data)

## 📊 Monitoramento

### Ver status
```bash
sudo systemctl status kairos-rastreio.service
```

### Ver logs em tempo real
```bash
sudo journalctl -u kairos-rastreio.service -f
```

### Reiniciar
```bash
sudo systemctl restart kairos-rastreio.service
```

### Verificar portas
```bash
sudo netstat -tlnp | grep -E ":(80|443|8000)"
```

## 🆘 Troubleshooting Comum

| Problema | Causa | Solução |
|----------|-------|---------|
| 502 Bad Gateway | Gunicorn não respondendo | `sudo systemctl restart kairos-rastreio.service` |
| 404 arquivos estáticos | Path incorreto do static | Verificar `/var/www/kairos-rastreio/static/` existe |
| Conexão recusada na porta 8000 | Firewall bloqueando | Verificar regras UFW |
| Certificado SSL inválido | Certbot não rodou ou domínio errado | `sudo certbot --nginx -d seu_dominio.com` |
| Permissão negada em arquivo | Proprietário errado | `sudo chown -R www-data:www-data /var/www/kairos-rastreio` |

## 📚 Arquivos de Documentação

- **DEPLOYMENT.md**: Guia passo a passo completo
- **QUICK-START.md**: Referência rápida com comandos essenciais  
- **SECURITY.md**: Checklist de segurança e otimizações
- **ARCHITECTURE.md**: Diagrama detalhado (próximo arquivo)

## 🔗 Referências

- [Flask Official Docs](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt](https://letsencrypt.org/)
- [Systemd Documentation](https://systemd.io/)

## 📞 Suporte

Para problemas específicos, consulte:
1. Logs da aplicação: `journalctl -u kairos-rastreio.service -n 50`
2. Logs do Nginx: `/var/log/nginx/kairos-rastreio-error.log`
3. Documentação em `DEPLOYMENT.md`
4. Troubleshooting em `SECURITY.md`

---

**Última atualização**: Março de 2026
