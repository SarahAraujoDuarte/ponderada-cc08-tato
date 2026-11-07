"""Versão 1: buffer circular com contador compartilhado e sem sincronização.

O ``sleep(0)`` entre a leitura e a escrita de ``ocupadas`` força trocas de
contexto no pior momento e torna observável a condição de corrida solicitada.

Autora: Sarah Araujo Duarte
Disciplina: Computação CC08
"""

from __future__ import annotations

import argparse
import threading
import time

from comum import (
    TAMANHO_BUFFER,
    TIMEOUT_SEGUNDOS,
    TOTAL_PADRAO,
    calcular_resultado,
    imprimir_resultado,
)


def executar(total: int) -> tuple[list[object], bool]:
    """Executa produtor e consumidor sem proteger o estado compartilhado.

    Args:
        total: Número de amostras sequenciais que o produtor deve gerar.

    Returns:
        Uma tupla com os valores retirados do buffer e o indicador de travamento.
    """

    buffer: list[object] = [None] * TAMANHO_BUFFER
    recebidas: list[object] = []
    parar = threading.Event()
    estado = {"escrita": 0, "leitura": 0, "ocupadas": 0}
    travou = False

    def produtor() -> None:
        """Insere IDs no buffer; lê e grava o contador em operações separadas."""

        for amostra in range(total):
            while estado["ocupadas"] >= TAMANHO_BUFFER and not parar.is_set():
                time.sleep(0)
            if parar.is_set():
                return

            indice = estado["escrita"]
            buffer[indice] = amostra
            estado["escrita"] = (indice + 1) % TAMANHO_BUFFER

            valor_lido = estado["ocupadas"]
            time.sleep(0)
            estado["ocupadas"] = valor_lido + 1

    def consumidor() -> None:
        """Retira itens por espera ocupada e aciona o watchdog após um segundo."""

        nonlocal travou
        ultimo_progresso = time.monotonic()

        while len(recebidas) < total:
            if estado["ocupadas"] <= 0:
                if time.monotonic() - ultimo_progresso >= TIMEOUT_SEGUNDOS:
                    travou = True
                    parar.set()
                    return
                time.sleep(0)
                continue

            indice = estado["leitura"]
            recebidas.append(buffer[indice])
            buffer[indice] = None
            estado["leitura"] = (indice + 1) % TAMANHO_BUFFER

            valor_lido = estado["ocupadas"]
            time.sleep(0)
            estado["ocupadas"] = valor_lido - 1
            ultimo_progresso = time.monotonic()

    thread_produtor = threading.Thread(target=produtor, name="sensor", daemon=True)
    thread_consumidor = threading.Thread(target=consumidor, name="motor", daemon=True)
    thread_produtor.start()
    thread_consumidor.start()
    thread_consumidor.join(timeout=10.0)

    if thread_consumidor.is_alive():
        travou = True
        parar.set()

    thread_produtor.join(timeout=0.1)
    return recebidas, travou


def ler_argumentos() -> argparse.Namespace:
    """Lê a quantidade opcional de amostras informada na linha de comando.

    Returns:
        Namespace com ``amostras`` validado como inteiro positivo.
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--amostras", type=int, default=TOTAL_PADRAO)
    argumentos = parser.parse_args()
    if argumentos.amostras <= 0:
        parser.error("--amostras deve ser positivo")
    return argumentos


if __name__ == "__main__":
    args = ler_argumentos()
    valores, houve_travamento = executar(args.amostras)
    metricas = calcular_resultado(valores, args.amostras, houve_travamento)
    imprimir_resultado("Versão 1 — sem sincronização", args.amostras, metricas)
