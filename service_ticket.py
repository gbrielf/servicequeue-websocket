from fastapi import FastAPI
app = FastAPI()

# Simulação de Banco de Dados
fila = ["A10", "A11", "A12", "A13", "A14"]
senha_atual = "---"
ultimo_numero = 14  # Ajustado para refletir a última senha na fila


@app.get("/fila")
def ler_fila():
    return {
        "proximo": fila[0] if fila else None, 
        "tamanho": len(fila),
        "atual": senha_atual,
        "lista_completa": fila
    }


@app.post("/chamar")
def chamar_proximo():
    global senha_atual
    if fila:
        senha_atual = fila.pop(0)
    return {"senha": senha_atual}


@app.post("/entrar")
def pegar_senha():
    global ultimo_numero
    ultimo_numero += 1
    nova_senha = f"A{ultimo_numero}"
    fila.append(nova_senha)
    return {"senha": nova_senha, "posicao": len(fila)}