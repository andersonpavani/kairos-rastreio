from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Rastreamento(db.Model):
    """Modelo para armazenar informações de rastreamentos."""
    __tablename__ = 'rastreamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_venda = db.Column(db.String(17), nullable=True, index=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(100), default='não_consultado')  # não_consultado, em_transito, entregue, erro
    descricao = db.Column(db.Text, nullable=True)
    data = db.Column(db.String(100), nullable=True)
    local = db.Column(db.String(255), nullable=True)
    destino = db.Column(db.String(255), nullable=True)
    dados_completos = db.Column(db.JSON, nullable=True)  # Armazenar resposta completa da API
    ultima_consulta = db.Column(db.DateTime, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<Rastreamento {self.codigo}>'
    
    def to_dict(self):
        """Converte o objeto para dicionário."""
        return {
            'id': self.id,
            'id_venda': self.id_venda,
            'codigo': self.codigo,
            'status': self.status,
            'descricao': self.descricao,
            'data': self.data,
            'local': self.local,
            'destino': self.destino,
            'ultima_consulta': self.ultima_consulta.strftime('%d/%m/%Y %H:%M:%S') if self.ultima_consulta else None,
            'data_criacao': self.data_criacao.strftime('%d/%m/%Y %H:%M:%S') if self.data_criacao else None,
            'dados_completos': self.dados_completos
        }
