import socket
import json
from datetime import datetime


class UDPMetricsClient:
    """Cliente UDP para enviar métricas sem bloquear a aplicação"""
    
    def __init__(self, server_host='127.0.0.1', server_port=9999):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Configurar timeout baixo para não bloquear
        self.sock.settimeout(0.1)
    
    def send_metric(self, event: str, data: dict, source: str):
        """
        Envia uma métrica via UDP
        
        Args:
            event: Tipo de evento (ex: 'senha_gerada', 'senha_chamada')
            data: Dados do evento
            source: Origem do evento (ex: 'service_ticket', 'gateway')
        """
        try:
            metric = {
                'event': event,
                'data': data,
                'source': source,
                'timestamp': datetime.now().isoformat()
            }
            message = json.dumps(metric).encode('utf-8')
            self.sock.sendto(message, (self.server_host, self.server_port))
        except Exception as e:
            # Falhas no envio de métricas não devem quebrar o serviço
            # Apenas log silencioso (ou pode ser removido em produção)
            pass
    
    def close(self):
        self.sock.close()
