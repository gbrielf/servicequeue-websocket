from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/estatisticas")
def ler_stats(pessoas_na_frente: int = Query(0)):
    tempo_estimado = pessoas_na_frente * 15

    return {
        "tempo_medio_espera_minutos": tempo_estimado,
        "mensagem": "Cálculo baseado em 15min por pessoa"
    }