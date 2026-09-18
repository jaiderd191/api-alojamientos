def test_health_responde_200(client):
    respuesta = client.get("/health")

    assert respuesta.status_code == 200


def test_health_responde_json_esperado(client):
    respuesta = client.get("/health")
    datos = respuesta.get_json()

    assert respuesta.content_type.startswith("application/json")
    assert datos == {
        "status": "ok",
        "service": "alojamientos-api",
        "version": "v1",
    }
    def test_health_responde_200(client):
        respuesta = client.get("/health")

    assert respuesta.status_code == 200


def test_health_responde_json_esperado(client):
    respuesta = client.get("/health")
    datos = respuesta.get_json()

    assert respuesta.content_type.startswith("application/json")
    assert datos == {
        "status": "ok",
        "service": "alojamientos-api",
        "version": "v1",
    }


def test_health_expone_cors_para_origen_permitido(client):
    respuesta = client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )

    assert respuesta.headers.get("Access-Control-Allow-Origin") == (
        "http://localhost:5173"
    )