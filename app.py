import sys
import requests
import json
import os
from datetime import datetime


def format_tracking_info(data):
    """Formata as informações de rastreamento de forma legível."""
    print("\n" + "="*60)
    print("INFORMAÇÕES DE RASTREAMENTO")
    print("="*60 + "\n")
    
    # Informações básicas
    if 'codigo' in data:
        print(f"Código de Rastreamento: {data['codigo']}")
    if 'status' in data:
        print(f"Status: {data['status']}")
    if 'situacao' in data:
        print(f"Situação: {data['situacao']}")
    
    # Detalhes da encomenda
    if 'recebedor' in data:
        print(f"\nDestinatário: {data['recebedor']}")
    if 'remetente' in data:
        print(f"Remetente: {data['remetente']}")
    if 'tipo_postagem' in data:
        print(f"Tipo de Postagem: {data['tipo_postagem']}")
    if 'peso' in data:
        print(f"Peso: {data['peso']}")
    
    # Datas importantes
    if 'data_postagem' in data:
        print(f"\nData de Postagem: {data['data_postagem']}")
    if 'data_entrega' in data:
        print(f"Data de Entrega: {data['data_entrega']}")
    if 'data_atualizacao' in data:
        print(f"Última Atualização: {data['data_atualizacao']}")
    
    # Histórico de rastreamento
    if 'historico' in data and data['historico']:
        print("\n" + "-"*60)
        print("HISTÓRICO DE RASTREAMENTO")
        print("-"*60)
        for evento in data['historico']:
            if isinstance(evento, dict):
                data_evento = evento.get('data', 'N/A')
                status_evento = evento.get('status', 'N/A')
                local = evento.get('local', 'N/A')
                detalhes = evento.get('detalhes', '')
                
                print(f"\n📅 {data_evento}")
                print(f"   Status: {status_evento}")
                print(f"   Local: {local}")
                if detalhes:
                    print(f"   Detalhes: {detalhes}")
    
    print("\n" + "="*60 + "\n")


def track_package(codigo, token=None):
    """
    Consulta a API do SiteRastreio para obter informações de rastreamento.
    
    Args:
        codigo (str): Código de rastreamento da encomenda
        token (str): Token bearer para autenticação na API (opcional)
    
    Returns:
        dict: Dados de rastreamento da encomenda
    """
    url = f"https://seurastreio.com.br/api/public/rastreio/{codigo}"
    
    try:
        print(f"\n🔄 Consultando informações de rastreamento para: {codigo}")
        print("Por favor, aguarde...\n")
        
        # Preparar headers com token bearer se fornecido
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
            print(f"✅ Usando token de autenticação\n")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'success' in data and data['success']:
                return data.get('data', data)
            elif 'erro' not in data or not data['erro']:
                return data
            else:
                print(f"❌ Erro: {data.get('erro', 'Erro desconhecido')}")
                return None
        
        elif response.status_code == 404:
            print(f"❌ Código de rastreamento '{codigo}' não encontrado!")
            return None
        
        else:
            print(f"❌ Erro na requisição: Status {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout na requisição (conexão expirou)")
        return None
    
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Falha na conexão com o servidor")
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {str(e)}")
        return None
    
    except json.JSONDecodeError:
        print("❌ Erro: Resposta da API não é um JSON válido")
        return None


def main():
    """Função principal do aplicativo."""
    
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("RASTREADOR DE ENCOMENDAS - SiteRastreio")
        print("="*60)
        print("\nUso: python app.py <codigo_rastreamento> [token]")
        print("\nExemplos:")
        print("  python app.py AD135095995BR")
        print("  python app.py AD135095995BR seu_token_aqui")
        print("\nNota: O token também pode ser definido na variável de ambiente SITERASTREIO_TOKEN")
        print("="*60 + "\n")
        sys.exit(1)
    
    codigo = sys.argv[1].strip().upper()
    
    # Obter token do argumento ou variável de ambiente
    token = None
    if len(sys.argv) > 2:
        token = sys.argv[2].strip()
    else:
        token = os.getenv('SITERASTREIO_TOKEN')
    
    # Consultar a API
    resultado = track_package(codigo, token=token)
    
    if resultado:
        format_tracking_info(resultado)
        
        # Opcionalmente, salvar resultado em JSON
        try:
            with open(f"rastreamento_{codigo}.json", "w", encoding="utf-8") as f:
                json.dump(resultado, f, ensure_ascii=False, indent=2)
            print(f"✅ Dados salvos em: rastreamento_{codigo}.json\n")
        except Exception as e:
            print(f"⚠️  Não foi possível salvar o arquivo: {str(e)}\n")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
