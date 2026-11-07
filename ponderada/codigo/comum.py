"""Utilitários de medição para as três versões do buffer da questão A4.

Autora: Sarah Araujo Duarte
Disciplina: Computação CC08
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


TOTAL_PADRAO = 20_000
TAMANHO_BUFFER = 5
TIMEOUT_SEGUNDOS = 1.0


@dataclass(frozen=True)
class Resultado:
    """Armazena as métricas finais de uma execução.

    Atributos:
        consumidas: Quantidade total de leituras válidas feitas pelo consumidor.
        perdidas: IDs esperados que não apareceram nenhuma vez.
        duplicadas: Leituras válidas além da primeira ocorrência de cada ID.
        travou: Indica se o consumidor passou um segundo sem receber uma amostra.
    """

    consumidas: int
    perdidas: int
    duplicadas: int
    travou: bool


def calcular_resultado(recebidas: Iterable[object], total: int, travou: bool) -> Resultado:
    """Calcula perdas e duplicações a partir dos valores lidos.

    Args:
        recebidas: Valores retirados do buffer pelo consumidor.
        total: Quantidade de IDs válidos esperados, de zero até ``total - 1``.
        travou: Se o watchdog de um segundo detectou falta de progresso.

    Returns:
        Um ``Resultado`` com quantidade válida consumida, perdas, duplicações e
        estado de travamento. Valores ``None`` ou fora da faixa são descartados.
    """

    validas = [valor for valor in recebidas if isinstance(valor, int) and 0 <= valor < total]
    unicas = set(validas)
    return Resultado(
        consumidas=len(validas),
        perdidas=total - len(unicas),
        duplicadas=len(validas) - len(unicas),
        travou=travou,
    )


def imprimir_resultado(versao: str, total: int, resultado: Resultado) -> None:

    """Imprime uma linha estável, adequada para a tabela e os prints da entrega.

    Args:
        versao: Nome legível da implementação executada.
        total: Quantidade de amostras que deveriam ser produzidas.
        resultado: Métricas calculadas pela execução.

    Returns:
        Nada. A função escreve o resumo diretamente na saída padrão.
    """

    estado = "sim" if resultado.travou else "não"
    print(
        f"{versao} | N={TAMANHO_BUFFER} | produzidas={total} | "
        f"consumidas={resultado.consumidas} | perdidas={resultado.perdidas} | "
        f"duplicadas={resultado.duplicadas} | travou={estado}"
    )

