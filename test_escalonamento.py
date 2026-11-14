import unittest

from escalonamento import fcfs, sjf, srtf, round_robin, validar_processos


class TestesEscalonamento(unittest.TestCase):
    def setUp(self):
        self.processos = [
            ("P1", 0, 7),
            ("P2", 2, 4),
            ("P3", 4, 1),
            ("P4", 5, 4),
        ]

    def test_srtf_preempta_processo_atual(self):
        resultado = srtf(self.processos)
        self.assertEqual(
            resultado["gantt"],
            [(0, 2, "P1"), (2, 4, "P2"), (4, 5, "P3"),
             (5, 7, "P2"), (7, 11, "P4"), (11, 16, "P1")]
        )
        self.assertEqual(
            [m["conclusao"] for m in resultado["metricas"]],
            [16, 7, 5, 11]
        )

    def test_fcfs_ordem_de_chegada_e_idle(self):
        resultado = fcfs([("A", 3, 2), ("B", 4, 1)])
        self.assertEqual(resultado["gantt"], [(0, 3, "IDLE"), (3, 5, "A"), (5, 6, "B")])

    def test_sjf_nao_preemptivo(self):
        resultado = sjf(self.processos)
        self.assertEqual(resultado["gantt"][0], (0, 7, "P1"))
        self.assertEqual(resultado["gantt"][1][2], "P3")

    def test_round_robin_quantum(self):
        resultado = round_robin([("A", 0, 5), ("B", 1, 2)], 2)
        self.assertEqual(resultado["gantt"], [
            (0, 2, "A"), (2, 4, "B"), (4, 7, "A")
        ])

    def test_validacao(self):
        with self.assertRaises(ValueError):
            validar_processos([("A", -1, 2)])
        with self.assertRaises(ValueError):
            validar_processos([("A", 0, 0)])
        with self.assertRaises(ValueError):
            validar_processos([("A", 0, 1), ("A", 2, 3)])

    def test_medias(self):
        resultado = fcfs([("A", 0, 3), ("B", 1, 2)])
        self.assertEqual(resultado["espera_media"], 1.0)
        self.assertEqual(resultado["retorno_medio"], 3.5)


if __name__ == "__main__":
    unittest.main()
