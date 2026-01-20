from fastapi import FastAPI, Query
from udp_client import UDPMetricsClient

app = FastAPI()

# Cliente UDP para envio de métricas
metrics_client = UDPMetricsClient()


@app.get("/estatisticas")
def ler_stats(pessoas_na_frente: int = Query(0)):
    tempo_estimado = pessoas_na_frente * 15
    
    # Enviar métrica via UDP
    metrics_client.send_metric(
        event='consulta_estatisticas',
        data={
            'pessoas_na_frente': pessoas_na_frente,
            'tempo_estimado_minutos': tempo_estimado
        },
        source='service_stats'
    )

    return {
        "tempo_medio_espera_minutos": tempo_estimado,
        "mensagem": "Cálculo baseado em 15min por pessoa"
    }