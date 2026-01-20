import socket
import json
from datetime import datetime
from collections import defaultdict
from threading import Thread
import time


class MetricsCollector:
    def __init__(self):
        self.metrics = defaultdict(int)
        self.events = []
        self.start_time = datetime.now()
        
    def record_event(self, event_type: str, data: dict):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.events.append({
            "timestamp": timestamp,
            "type": event_type,
            "data": data
        })
        self.metrics[event_type] += 1
        
        # Manter apenas os últimos 100 eventos
        if len(self.events) > 100:
            self.events.pop(0)
    
    def get_summary(self):
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "uptime_seconds": round(uptime, 2),
            "total_events": sum(self.metrics.values()),
            "events_by_type": dict(self.metrics),
            "recent_events": self.events[-10:]  # Últimos 10 eventos
        }
    
    def print_stats(self):
        summary = self.get_summary()
        print(f"\n{'='*60}")
        print(f"📊 ESTATÍSTICAS DO SISTEMA - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        print(f"⏱️  Tempo ativo: {summary['uptime_seconds']:.0f}s")
        print(f"📈 Total de eventos: {summary['total_events']}")
        print(f"\n📋 Eventos por tipo:")
        for event_type, count in summary['events_by_type'].items():
            print(f"   • {event_type}: {count}")
        print(f"{'='*60}\n")


class UDPMetricsServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.collector = MetricsCollector()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        self.running = False
        
    def start(self):
        self.running = True
        print(f"🚀 Servidor UDP de Métricas iniciado em {self.host}:{self.port}")
        print(f"📡 Aguardando métricas dos serviços...\n")
        
        # Thread para exibir estatísticas periodicamente
        stats_thread = Thread(target=self.periodic_stats, daemon=True)
        stats_thread.start()
        
        # Loop principal para receber métricas
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.process_metric(data, addr)
            except Exception as e:
                print(f"❌ Erro ao processar métrica: {e}")
    
    def process_metric(self, data: bytes, addr: tuple):
        try:
            metric = json.loads(data.decode('utf-8'))
            event_type = metric.get('event', 'unknown')
            event_data = metric.get('data', {})
            source = metric.get('source', 'unknown')
            
            # Registrar o evento
            self.collector.record_event(event_type, {
                **event_data,
                'source': source,
                'from': f"{addr[0]}:{addr[1]}"
            })
            
            # Exibir evento em tempo real
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 📨 {event_type.upper()} - {source}")
            if event_data:
                for key, value in event_data.items():
                    print(f"         └─ {key}: {value}")
            
        except json.JSONDecodeError:
            print(f"⚠️  Dados inválidos recebidos de {addr}")
    
    def periodic_stats(self):
        """Exibe estatísticas a cada 30 segundos"""
        while self.running:
            time.sleep(30)
            self.collector.print_stats()
    
    def stop(self):
        self.running = False
        self.sock.close()
        print("🛑 Servidor UDP encerrado")


if __name__ == "__main__":
    server = UDPMetricsServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\n\n⏹️  Encerrando servidor...")
        server.collector.print_stats()
        server.stop()
