from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from models import db, Rastreamento

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rastreamentos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
db.init_app(app)

# Obter token da variável de ambiente
TOKEN = os.getenv('SITERASTREIO_TOKEN', '')


# Criar tabelas se não existirem
with app.app_context():
    db.create_all()


def track_package(codigo, token=None):
    """
    Consulta a API do SiteRastreio para obter informações de rastreamento.
    
    Args:
        codigo (str): Código de rastreamento da encomenda
        token (str): Token bearer para autenticação na API (opcional)
    
    Returns:
        tuple: (dados, erro) - dados de rastreamento ou mensagem de erro
    """
    url = f"https://seurastreio.com.br/api/public/rastreio/{codigo}"
    
    try:
        # Preparar headers com token bearer se fornecido
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'success' in data and data['success']:
                return data.get('data', data), None
            elif 'erro' not in data or not data['erro']:
                return data, None
            else:
                return None, f"Erro: {data.get('erro', 'Erro desconhecido')}"
        
        elif response.status_code == 404:
            return None, f"Código de rastreamento '{codigo}' não encontrado!"
        
        elif response.status_code == 401:
            return None, "Erro de autenticação! Token inválido ou expirado."
        
        elif response.status_code == 403:
            return None, "Acesso negado! Verifique se o token possui as permissões necessárias."
        
        else:
            return None, f"Erro na requisição: Status {response.status_code}"
    
    except requests.exceptions.Timeout:
        return None, "Erro: Timeout - conexão expirou. Tente novamente."
    
    except requests.exceptions.ConnectionError:
        return None, "Erro: Falha na conexão com o servidor. Verifique sua conexão de internet."
    
    except requests.exceptions.RequestException as e:
        return None, f"Erro na requisição: {str(e)}"
    
    except json.JSONDecodeError:
        return None, "Erro: Resposta da API não é um JSON válido"


def extrair_informacoes(dados):
    """
    Extrai as informações relevantes dos dados da API.
    
    Returns:
        dict com status, descricao, data, local, destino
    """
    resultado = {
        'status': 'desconhecido',
        'descricao': 'Sem informações',
        'data': None,
        'local': None,
        'destino': None
    }
    
    if not isinstance(dados, dict):
        return resultado
    
    # Extrair status geral
    if 'status' in dados:
        status_api = dados['status'].lower()
        if status_api == 'found':
            resultado['status'] = 'em_transito'
    
    # Verificar se há eventoMaisRecente (novo formato da API)
    if 'eventoMaisRecente' in dados and isinstance(dados['eventoMaisRecente'], dict):
        evento = dados['eventoMaisRecente']
        
        # Extrair descrição
        if 'descricao' in evento:
            resultado['descricao'] = evento['descricao']
        
        # Extrair data
        if 'data' in evento:
            # Formatar data se estiver em formato ISO
            data_str = evento['data']
            if 'T' in data_str:
                # Converter de 2026-02-26T06:39:30 para 26/02/2026 06:39
                try:
                    data_obj = datetime.fromisoformat(data_str)
                    resultado['data'] = data_obj.strftime('%d/%m/%Y %H:%M')
                except:
                    resultado['data'] = data_str
            else:
                resultado['data'] = data_str
        
        # Extrair local
        if 'local' in evento:
            resultado['local'] = evento['local']
        
        # Extrair destino
        if 'destino' in evento:
            resultado['destino'] = evento['destino']
    
    # Fallback: tentar extrair de campos antigos (compatibilidade)
    else:
        # Extrair descrição
        if 'situacao' in dados:
            resultado['descricao'] = dados['situacao']
        elif 'status' in dados and isinstance(dados['status'], str):
            resultado['status'] = dados['status']
        
        # Extrair destino
        if 'recebedor' in dados:
            resultado['destino'] = dados['recebedor']
        
        # Extrair data e local do histórico mais recente
        if 'historico' and isinstance(dados.get('historico'), list) and len(dados['historico']) > 0:
            evento_recente = dados['historico'][0]
            if isinstance(evento_recente, dict):
                if 'data' in evento_recente:
                    resultado['data'] = evento_recente['data']
                if 'local' in evento_recente:
                    resultado['local'] = evento_recente['local']
                if 'status' in evento_recente:
                    resultado['status'] = evento_recente['status']
    
    return resultado


@app.route('/')
def index():
    """Página principal com painel de rastreamentos."""
    tem_token = bool(TOKEN)
    return render_template('dashboard.html', tem_token=tem_token)


@app.route('/api/rastreamentos', methods=['GET'])
def get_rastreamentos():
    """Retorna todos os rastreamentos ordenados pelo mais recente primeiro."""
    rastreamentos = Rastreamento.query.order_by(Rastreamento.data_criacao.desc()).all()
    return jsonify({
        'sucesso': True,
        'rastreamentos': [r.to_dict() for r in rastreamentos]
    })


@app.route('/api/rastreamentos', methods=['POST'])
def criar_rastreamento():
    """Cria um novo rastreamento sem consultar a API imediatamente."""
    data = request.get_json()
    codigo = data.get('codigo', '').strip().upper()
    
    if not codigo:
        return jsonify({'erro': 'Código é obrigatório'}), 400
    
    # Verificar se já existe
    existente = Rastreamento.query.filter_by(codigo=codigo).first()
    if existente:
        return jsonify({'erro': f'Código {codigo} já foi adicionado'}), 400
    
    # Criar novo rastreamento
    novo = Rastreamento(codigo=codigo)
    db.session.add(novo)
    db.session.commit()
    
    return jsonify({
        'sucesso': True,
        'rastreamento': novo.to_dict()
    }), 201


@app.route('/api/rastreamentos/<int:id>', methods=['DELETE'])
def deletar_rastreamento(id):
    """Deleta um rastreamento."""
    rastreamento = Rastreamento.query.get(id)
    
    if not rastreamento:
        return jsonify({'erro': 'Rastreamento não encontrado'}), 404
    
    db.session.delete(rastreamento)
    db.session.commit()
    
    return jsonify({'sucesso': True})


@app.route('/api/rastreamentos/<int:id>/consultar', methods=['POST'])
def consultar_rastreamento(id):
    """Consulta a API para um rastreamento específico."""
    rastreamento = Rastreamento.query.get(id)
    
    if not rastreamento:
        return jsonify({'erro': 'Rastreamento não encontrado'}), 404
    
    # Se já foi entregue, não consultar novamente
    if rastreamento.status == 'entregue':
        return jsonify({
            'sucesso': True,
            'mensagem': 'Rastreamento já finalizado',
            'rastreamento': rastreamento.to_dict()
        })
    
    # Consultar API
    dados, erro = track_package(rastreamento.codigo, token=TOKEN if TOKEN else None)
    
    if erro:
        rastreamento.status = 'erro'
        rastreamento.descricao = erro
        db.session.commit()
        return jsonify({
            'sucesso': False,
            'erro': erro,
            'rastreamento': rastreamento.to_dict()
        }), 400
    else:
        # Extrair informações
        info = extrair_informacoes(dados)
        rastreamento.status = info['status']
        rastreamento.descricao = info['descricao']
        rastreamento.data = info['data']
        rastreamento.local = info['local']
        rastreamento.destino = info['destino']
        rastreamento.dados_completos = dados
        
        # Definir como entregue se a descrição indicar
        descricao = rastreamento.descricao.lower() if rastreamento.descricao else ''
        if 'entregue' in descricao or 'recebido' in descricao or 'entregação' in descricao:
            rastreamento.status = 'entregue'
        
        # Só atualizar ultima_consulta em caso de sucesso
        rastreamento.ultima_consulta = datetime.now()
    
    db.session.commit()
    
    return jsonify({
        'sucesso': True,
        'rastreamento': rastreamento.to_dict()
    })


@app.route('/api/rastreamentos/atualizar-todos', methods=['POST'])
def atualizar_todos():
    """Atualiza todos os rastreamentos que ainda não foram consultados ou estão em trânsito."""
    rastreamentos = Rastreamento.query.filter(
        Rastreamento.status != 'entregue'
    ).all()
    
    resultados = []
    
    for rastreamento in rastreamentos:
        # Consultar API
        dados, erro = track_package(rastreamento.codigo, token=TOKEN if TOKEN else None)
        
        if erro:
            rastreamento.status = 'erro'
            rastreamento.descricao = erro
        else:
            # Extrair informações
            info = extrair_informacoes(dados)
            rastreamento.status = info['status']
            rastreamento.descricao = info['descricao']
            rastreamento.data = info['data']
            rastreamento.local = info['local']
            rastreamento.destino = info['destino']
            rastreamento.dados_completos = dados
            
            # Definir como entregue se a descrição indicar
            descricao = rastreamento.descricao.lower() if rastreamento.descricao else ''
            if 'entregue' in descricao or 'recebido' in descricao or 'entregação' in descricao:
                rastreamento.status = 'entregue'
            
            # Só atualizar ultima_consulta em caso de sucesso
            rastreamento.ultima_consulta = datetime.now()
        
        resultados.append(rastreamento.to_dict())
    
    db.session.commit()
    
    return jsonify({
        'sucesso': True,
        'total': len(resultados),
        'rastreamentos': resultados
    })


@app.route('/api/status')
def api_status():
    """Retorna informações sobre a aplicação."""
    return jsonify({
        'app': 'Rastreador SiteRastreio',
        'versao': '2.0.0',
        'autenticacao': 'com_token' if TOKEN else 'sem_token',
        'status': 'online'
    })


@app.errorhandler(404)
def nao_encontrado(error):
    """Handler para página não encontrada."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def erro_servidor(error):
    """Handler para erro interno do servidor."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Rastreador SiteRastreio - App Web v2.0")
    print("="*60)
    print("\n✅ Servidor iniciado com sucesso!")
    print("📍 Acesse: http://localhost:5000")
    print("🔐 Autenticação: " + ("COM token" if TOKEN else "SEM token"))
    print("💾 Banco de dados: rastreamentos.db")
    print("\nPressione CTRL+C para parar o servidor\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
