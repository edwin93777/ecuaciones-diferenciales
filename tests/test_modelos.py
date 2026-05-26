from __future__ import annotations

import math
import unittest

from backend.modelos.crecimiento import resolver_crecimiento
from backend.modelos.decaimiento import resolver_decaimiento
from backend.modelos.enfriamiento import resolver_enfriamiento
from backend.modelos.mezclas import resolver_mezclas


class TestModelosPorModulo(unittest.TestCase):
    def assert_aproximado(self, obtenido: float, esperado: float, tolerancia: float = 1e-5) -> None:
        self.assertTrue(math.isclose(float(obtenido), esperado, rel_tol=tolerancia, abs_tol=tolerancia), f"{obtenido} != {esperado}")

    def test_crecimiento_proporcional_evalua_variante(self):
        resultado = resolver_crecimiento({
            "variante": "crecimiento_proporcional",
            "tipo_calculo": "valor_en_tiempo",
            "cantidad_inicial": 500,
            "tiempo_transcurrido": 4,
            "cantidad_transcurrida": 900,
            "tiempo_objetivo": 8,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["modulo"], "crecimiento")
        self.assertEqual(resultado["variante"], "crecimiento_proporcional")
        self.assert_aproximado(resultado["resultado"], 1620)

    def test_crecimiento_interes_continuo_como_variante(self):
        resultado = resolver_crecimiento({
            "variante": "interes_continuo",
            "tipo_calculo": "valor_en_tiempo",
            "capital_inicial": 2000,
            "tasa_porcentual": 6,
            "tiempo_objetivo": 5,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["modulo"], "crecimiento")
        self.assertEqual(resultado["variante"], "interes_continuo")
        self.assert_aproximado(resultado["resultado"], 2000 * math.exp(0.06 * 5))

    def test_crecimiento_con_entrada_constante(self):
        resultado = resolver_crecimiento({
            "variante": "entrada_constante",
            "tipo_calculo": "valor_en_tiempo",
            "cantidad_inicial": 100,
            "constante_k": 0.04,
            "entrada_constante": 50,
            "tiempo_objetivo": 2,
        })
        esperado = (100 + 50 / 0.04) * math.exp(0.04 * 2) - 50 / 0.04
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["modulo"], "crecimiento")
        self.assert_aproximado(resultado["resultado"], esperado)

    def test_caida_resistencia_como_variante_lineal(self):
        resultado = resolver_crecimiento({
            "variante": "caida_resistencia",
            "tipo_calculo": "velocidad_limite",
            "velocidad_inicial": 0,
            "gravedad": 9.8,
            "constante_k": 0.25,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["modulo"], "crecimiento")
        self.assert_aproximado(resultado["resultado"], 39.2)


    def test_crecimiento_sin_k_responde_simbolico(self):
        resultado = resolver_crecimiento({
            "variante": "crecimiento_proporcional",
            "tipo_calculo": "valor_en_tiempo",
            "cantidad_inicial": 500,
            "tiempo_objetivo": 8,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "formula_simbolica")
        self.assertIn("k", str(resultado["resultado"]))

    def test_entrada_constante_sin_k_responde_simbolico(self):
        resultado = resolver_crecimiento({
            "variante": "entrada_constante",
            "tipo_calculo": "valor_en_tiempo",
            "cantidad_inicial": 100,
            "entrada_constante": 50,
            "tiempo_objetivo": 10,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "formula_simbolica")
        self.assertIn("k", str(resultado["resultado"]))

    def test_caida_resistencia_sin_k_responde_velocidad_limite_simbolica(self):
        resultado = resolver_crecimiento({
            "variante": "caida_resistencia",
            "tipo_calculo": "velocidad_limite",
            "gravedad": 9.8,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "formula_simbolica")
        self.assertIn("k", str(resultado["resultado"]))

    def test_descarga_capacitor_sin_rc_opera_simbolicamente(self):
        resultado = resolver_decaimiento({
            "variante": "descarga_capacitor",
            "tipo_calculo": "valor_en_tiempo",
            "cantidad_inicial": 10,
            "tiempo_objetivo": 5,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "formula_simbolica")
        self.assertIn("RC", str(resultado["resultado"]).replace(" ", ""))

    def test_descarga_capacitor_con_rc_opera_numericamente(self):
        resultado = resolver_decaimiento({
            "variante": "descarga_capacitor",
            "tipo_calculo": "valor_en_tiempo",
            "cantidad_inicial": 10,
            "resistencia": 2,
            "capacitancia": 5,
            "tiempo_objetivo": 10,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "valor_en_tiempo")
        self.assert_aproximado(resultado["resultado"], 10 * math.exp(-10 / (2 * 5)))

    def test_enfriamiento_sin_k_responde_simbolico(self):
        resultado = resolver_enfriamiento({
            "variante": "newton_constante",
            "tipo_calculo": "temperatura",
            "temperatura_inicial": 80,
            "temperatura_ambiente": 20,
            "tiempo_objetivo": 20,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "formula_simbolica")
        self.assertIn("k", str(resultado["resultado"]))

    def test_decaimiento_vida_media(self):
        resultado = resolver_decaimiento({
            "variante": "decaimiento_radiactivo",
            "tipo_calculo": "vida_media",
            "cantidad_inicial": 100,
            "tiempo_transcurrido": 5,
            "cantidad_transcurrida": 60,
        })
        k = math.log(100 / 60) / 5
        esperado = math.log(2) / k
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["modulo"], "decaimiento")
        self.assert_aproximado(resultado["resultado"], esperado)

    def test_decaimiento_intensidad_luz_variante(self):
        resultado = resolver_decaimiento({
            "variante": "intensidad_luz",
            "tipo_calculo": "valor_en_tiempo",
            "cantidad_inicial": 100,
            "distancia_transcurrida": 5,
            "cantidad_transcurrida": 70,
            "distancia_objetivo": 10,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["variante"], "intensidad_luz")
        self.assert_aproximado(resultado["resultado"], 49)

    def test_enfriamiento_newton(self):
        resultado = resolver_enfriamiento({
            "variante": "newton_constante",
            "tipo_calculo": "temperatura",
            "temperatura_inicial": 80,
            "temperatura_ambiente": 20,
            "tiempo_transcurrido": 10,
            "temperatura_transcurrida": 50,
            "tiempo_objetivo": 20,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["modulo"], "enfriamiento")
        self.assert_aproximado(resultado["resultado"], 35)

    def test_mezclas_volumen_constante_limite(self):
        resultado = resolver_mezclas({
            "variante": "volumen_constante",
            "tipo_calculo": "limite",
            "sal_inicial": 10,
            "volumen_inicial": 100,
            "concentracion_entrada": 0.5,
            "caudal_entrada": 5,
            "caudal_salida": 5,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["modulo"], "mezclas")
        self.assert_aproximado(resultado["resultado"], 50)

    def test_mezclas_volumen_variable(self):
        resultado = resolver_mezclas({
            "variante": "volumen_variable",
            "tipo_calculo": "cantidad",
            "sal_inicial": 10,
            "volumen_inicial": 100,
            "concentracion_entrada": 0.5,
            "caudal_entrada": 6,
            "caudal_salida": 4,
            "tiempo_objetivo": 20,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["variante"], "volumen_variable")
        self.assertGreater(resultado["resultado"], 0)
        self.assertIn("volumen_actual", resultado["metadatos"])

    def test_mezclas_volumen_constante_con_concentracion_salida_fija(self):
        resultado = resolver_mezclas({
            "variante": "volumen_constante",
            "tipo_calculo": "cantidad",
            "sal_inicial": 10,
            "volumen_inicial": 100,
            "concentracion_entrada": 0.5,
            "concentracion_salida": 0.2,
            "caudal_entrada": 5,
            "caudal_salida": 5,
            "tiempo_objetivo": 20,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "cantidad")
        self.assert_aproximado(resultado["resultado"], 40)
        self.assertIn("concentracion_salida", resultado["constantes"])

    def test_mezclas_volumen_variable_con_concentracion_salida_fija(self):
        resultado = resolver_mezclas({
            "variante": "volumen_variable",
            "tipo_calculo": "concentracion",
            "sal_inicial": 10,
            "volumen_inicial": 100,
            "concentracion_entrada": 0.5,
            "concentracion_salida": 0.2,
            "caudal_entrada": 6,
            "caudal_salida": 4,
            "tiempo_objetivo": 20,
        })
        self.assertNotIn("error", resultado)
        self.assertEqual(resultado["tipo"], "concentracion")
        self.assert_aproximado(resultado["resultado"], 54 / 140)
        self.assertIn("concentracion_salida", resultado["constantes"])


if __name__ == "__main__":
    unittest.main(verbosity=2)


def test_formula_simbolica_entrada_constante_con_datos_incompletos():
    respuesta = resolver_crecimiento({"variante": "entrada_constante", "tipo_calculo": "formula_simbolica", "cantidad_inicial": "100"})
    assert not respuesta.get("error")
    assert respuesta["tipo"] == "formula_simbolica"
    assert "P(t)" in respuesta["resultado"]


def test_formula_simbolica_descarga_capacitor_sin_rc():
    respuesta = resolver_decaimiento({"variante": "descarga_capacitor", "tipo_calculo": "formula_simbolica", "cantidad_inicial": "10"})
    assert not respuesta.get("error")
    assert respuesta["tipo"] == "formula_simbolica"
    assert "RC" in respuesta["resultado"]
