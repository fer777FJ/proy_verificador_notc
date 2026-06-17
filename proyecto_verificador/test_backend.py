import pytest
import json
from database import guardar_verificacion, serializar_fechas
from crear_csv import mapear_etiqueta

# ==========================================
# 1. PRUEBAS UNITARIAS: LÓGICA DE CONTROL
# ==========================================

def test_mapear_etiqueta_verdadero():
    """Caja Blanca: Verifica que 'verdadero' en cualquier formato devuelva 1"""
    assert mapear_etiqueta("Verdadero") == 1
    assert mapear_etiqueta("VERDADERO") == 1
    assert mapear_etiqueta("noticia verdadero") == 1

def test_mapear_etiqueta_falso():
    """Caja Blanca: Verifica que 'falso' devuelva 0"""
    assert mapear_etiqueta("Falso") == 0
    assert mapear_etiqueta("falso") == 0

def test_mapear_etiqueta_otros():
    """Caja Blanca: Verifica que cualquier otro veredicto devuelva -1 (ruido)"""
    assert mapear_etiqueta("Engañoso") == -1
    assert mapear_etiqueta("No determinado") == -1
    assert mapear_etiqueta("CualquierCosa") == -1

def test_serializar_fechas_exito():
    """Prueba que los objetos datetime se conviertan a strings ISO para FastAPI"""
    from datetime import datetime
    mock_data = [{"tipo": "texto", "fecha": datetime(2026, 6, 3, 12, 0, 0)}]
    resultado = serializar_fechas(mock_data)
    assert resultado[0]["fecha"] == "2026-06-03T12:00:00"

# ==========================================
# 2. PRUEBAS DE CAJA BLANCA: MANEJO DE ERRORES (Mocks)
# ==========================================

def test_guardar_verificacion_titulo_excedido():
    """Prueba que el sistema lance un ValueError si el título tiene > 255 caracteres"""
    datos_invalidos = {
        'titulo': "A" * 256,
        'contenido': "Contenido normal",
        'veredicto': 'Verdadero',
        'confianza': 0.85
    }
    with pytest.raises(ValueError) as exc_info:
        guardar_verificacion('texto', datos_invalidos)
    assert "El título excede los 255 caracteres" in str(exc_info.value)

def test_guardar_verificacion_veredicto_invalido():
    """Prueba que se rechacen veredictos no mapeados en la lista permitida de MariaDB"""
    datos_invalidos = {
        'titulo': "Titular Válido",
        'contenido': "Contenido",
        'veredicto': 'Verificado Pero En Desarrollo',  # ¡Ojo aquí!
        'confianza': 0.85
    }
    with pytest.raises(ValueError) as exc_info:
        guardar_verificacion('texto', datos_invalidos)
    assert "no es válido" in str(exc_info.value)