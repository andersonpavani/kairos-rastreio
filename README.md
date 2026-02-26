# 📦 Rastreador SiteRastreio

Aplicação web para rastreamento de encomendas usando a API do SiteRastreio.

## ✨ Características

- 🌐 Interface web moderna e responsiva
- 🔍 Rastreamento em tempo real
- 🔐 Suporte a autenticação com token bearer
- 📊 Exibição completa do histórico de movimentações
- ⚡ API REST integrada
- 📱 Design mobile-friendly

## 📁 Estrutura do Projeto

```
kairos-rastreio/
├── app.py              # CLI (Line Command Interface)
├── web_app.py          # Aplicação Flask
├── requirements.txt    # Dependências Python
├── .env.example        # Exemplo de variáveis de ambiente
├── templates/          # Templates HTML
│   ├── index.html      # Página principal
│   ├── 404.html        # Página de erro 404
│   └── 500.html        # Página de erro 500
├── static/             # Arquivos estáticos (CSS, JS)
└── env/                # Ambiente virtual Python
```

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Token (Opcional)

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione seu token:

```
SITERASTREIO_TOKEN=seu_token_aqui
```

### 3. Executar a Aplicação Web

```bash
python web_app.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 📋 Modo CLI (Linha de Comando)

Se preferir usar a CLI tradicional:

```bash
# Sem token
python app.py AN619556349BR

# Com token como argumento
python app.py AN619556349BR seu_token_aqui

# Com token de variável de ambiente
export SITERASTREIO_TOKEN="seu_token_aqui"
python app.py AN619556349BR
```

## 🔌 API REST

A aplicação também fornece endpoints REST:

### GET /api/rastreio/{codigo}

Consulta informações de rastreamento de uma encomenda.

**Exemplo:**
```bash
curl http://localhost:5000/api/rastreio/AN619556349BR
```

**Resposta:**
```json
{
  "sucesso": true,
  "dados": {
    "codigo": "AN619556349BR",
    "status": "Entregue",
    "situacao": "Objeto entregue ao destinatário",
    "historico": [...]
  }
}
```

### GET /api/status

Retorna informações sobre a aplicação.

```bash
curl http://localhost:5000/api/status
```

## ⚙️ Variáveis de Ambiente

```bash
SITERASTREIO_TOKEN  # Token de autenticação da API (opcional)
```

## 🔐 Autenticação

A aplicação suporta dois modos:

1. **Com Token**: Forneça credenciais válidas para acessar todos os recursos
2. **Sem Token**: Funcione em modo limitado (se a API permitir)

## 🎨 Interface Web

A interface web oferece:

- ✅ Campo de input para código de rastreamento
- ✅ Indicador de status de autenticação
- ✅ Exibição formatada de informações
- ✅ Timeline do histórico de movimentações
- ✅ Tratamento de erros amigável
- ✅ Design responsivo para mobile e desktop

## 📦 Dependências

- **Flask** - Framework web
- **requests** - Cliente HTTP
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"

Instale as dependências:
```bash
pip install -r requirements.txt
```

### Erro: "Connection refused"

Certifique-se de que a API do SiteRastreio está acessível.

### Erro: "Token inválido"

Verifique se o token está correto no arquivo `.env`.

## 📄 Licença

Este projeto é fornecido como está, para fins educacionais e de desenvolvimento.

---

**Criado para facilitar o rastreamento de encomendas! 🚚**
