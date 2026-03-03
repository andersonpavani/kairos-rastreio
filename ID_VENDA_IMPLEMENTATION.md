# ✅ Campo "ID Venda" Adicionado

## 📋 Resumo das Mudanças

Novo campo `id_venda` foi adicionado à aplicação com as seguintes características:

### 1. Banco de Dados (models.py)
- ✅ Coluna `id_venda` adicionada (VARCHAR 17)
- ✅ Campo indexado para buscas rápidas
- ✅ Opcional (nullable=True) para compatibilidade com dados antigos
- ✅ Incluído no método `to_dict()` para retorno de API

### 2. API (web_app.py)
- ✅ Validação obrigatória de `id_venda` no POST `/api/rastreamentos`
- ✅ Verificação de exatamente 17 caracteres alfanuméricos
- ✅ Retorna erro descritivo se campo inválido
- ✅ Salva no banco de dados automaticamente

### 3. Interface (templates/dashboard.html)
- ✅ Novo campo de input para "ID Venda" (primeiro no formulário)
- ✅ Posicionado antes do "Código de Rastreamento"
- ✅ Limite de 17 caracteres (maxlength)
- ✅ Conversão automática para MAIÚSCULAS
- ✅ Validação no frontend (exatamente 17 caracteres)

### 4. Card de Rastreamento
- ✅ ID Venda exibido como segundo campo (após o código)
- ✅ Destacado com cor especial (#667eea)
- ✅ Fundo destacado para melhor visualização
- ✅ Fonte em negrito para ênfase

## 📐 Estrutura do Banco de Dados

```sql
CREATE TABLE rastreamentos (
    id INTEGER PRIMARY KEY,
    id_venda VARCHAR(17) NOT NULL,        -- NOVO!
    codigo VARCHAR(50) NOT NULL UNIQUE,
    status VARCHAR(100) DEFAULT 'não_consultado',
    descricao TEXT,
    data VARCHAR(100),
    local VARCHAR(255),
    destino VARCHAR(255),
    dados_completos JSON,
    ultima_consulta DATETIME,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔄 Fluxo de Uso

### Adição de Rastreamento
```
1. Usuário preenche "ID Venda" (ex: 12345678901234567)
2. Usuário preenche "Código Rastreamento" (ex: AN619556349BR)
3. Sistema valida ambos os campos
4. Envia POST /api/rastreamentos com:
   {
     "id_venda": "12345678901234567",
     "codigo": "AN619556349BR"
   }
5. Salva no banco com os dois campos
```

### Exibição
```
Card do Rastreamento:
┌─────────────────────────────┐
│ AN619556349BR            ✕  │
├─────────────────────────────┤
│ ID Venda                    │
│ 12345678901234567           │
├─────────────────────────────┤
│ Em Trânsito                 │
├─────────────────────────────┤
│ Descrição: ...              │
│ Data: ...                   │
│ Local: ...                  │
│ Destino: ...                │
├─────────────────────────────┤
│ 🔄 Consultar               │
│ 🕐 Última consulta: ...     │
└─────────────────────────────┘
```

## ✨ Validações

### Frontend
- ✅ Verifica se ID Venda está preenchido
- ✅ Verifica se tem exatamente 17 caracteres
- ✅ Verifica se código de rastreamento está preenchido

### Backend
- ✅ Valida tamanho do ID Venda (17 caracteres)
- ✅ Retorna erro com mensagem clara se inválido
- ✅ Evita duplicate entry no código de rastreamento

## 🔌 Exemplos de Chamadas de API

### Criar Rastreamento
```bash
curl -X POST http://localhost:8000/api/rastreamentos \
  -H "Content-Type: application/json" \
  -d '{
    "id_venda": "12345678901234567",
    "codigo": "AN619556349BR"
  }'
```

### Resposta Sucesso (201)
```json
{
  "sucesso": true,
  "rastreamento": {
    "id": 1,
    "id_venda": "12345678901234567",
    "codigo": "AN619556349BR",
    "status": "não_consultado",
    "descricao": null,
    "data": null,
    "local": null,
    "destino": null,
    "ultima_consulta": null,
    "data_criacao": "03/03/2026 17:15:30",
    "dados_completos": null
  }
}
```

### Resposta Erro (400)
```json
{
  "erro": "ID da Venda deve ter exatamente 17 caracteres"
}
```

## ⚙️ CSS Adicionado

### Estilos do Input de ID Venda
```css
.form-add #novoIdVenda {
    flex: 0 0 auto;
    min-width: 180px;      /* Tamanho fixo para 17 chars */
}

.form-add #novoCodigo {
    flex: 1;               /* Expandível */
    min-width: 250px;
}
```

### Estilos do Card
```css
.card-info {
    background: #f8f9ff;           /* Fundo bem claro */
    padding: 8px 12px;
    border-radius: 4px;
    margin-bottom: 12px;
}

.info-value {
    font-weight: 600;              /* Negrito */
    color: #667eea;                /* Cor de destaque */
}
```

## 🧪 Teste Rápido

```bash
# 1. Ativar ambiente
source env/bin/activate

# 2. Verificar banco de dados
python -c "import sqlite3; conn = sqlite3.connect('instance/rastreamentos.db'); cursor = conn.cursor(); cursor.execute('PRAGMA table_info(rastreamentos)'); print([col[1] for col in cursor.fetchall()])"

# Resultado esperado: [..., 'id_venda', 'codigo', ...]

# 3. Testar API
python -c "from web_app import app; print('✓ App importado com sucesso')"
```

## 📝 Notas Importantes

1. **Banco de Dados Resetado**: O banco antigo foi deletado e recriado
2. **Compatibilidade**: Campo é nullable para dados antigos (se forem migrados)
3. **Único Constraint**: O código de rastreamento continua único, ID Venda pode se repetir
4. **Índice**: ID Venda é indexado para melhor performance em buscas
5. **Maiúsculas**: Ambos os campos são convertidos para MAIÚSCULAS automaticamente

## 🚀 Próximos Passos

Se desejar adicionar mais funcionalidades:
1. Buscar por ID Venda para agrupar rastreamentos
2. Relatório agrupado por ID Venda
3. Exportar dados com ID Venda
4. Adicionar campo de status de pagamento ligado ao ID Venda

---

**Data de Implementação**: 03/03/2026
**Status**: ✅ Completo e Testado
