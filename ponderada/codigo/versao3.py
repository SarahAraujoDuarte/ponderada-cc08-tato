"""Versão 3: ordem insegura — produtor adquire mutex antes de vazio.

Quando o buffer enche, o produtor pode manter ``mutex`` enquanto espera
``vazio``; o consumidor precisa do mesmo ``mutex`` para retirar uma amostra e
liberar uma vaga, criando espera circular.

Autora: Sarah Araujo Duarte
Disciplina: Computação CC08
"""

from __future__ import annotations

import argparse
import threading

from comum import (
    TAMANHO_BUFFER,
    TIMEOUT_SEGUNDOS,
    TOTAL_PADRAO,
    calcular_resultado,
    imprimir_resultado,
)


def executar(total: int) -> tuple[list[object], bool]:
    """Executa a variante sujeita a deadlock e observa-a com watchdog.

    Args:
        total: Número de amostras que o produtor tentará gerar.

    Returns:
        Uma tupla com os valores retirados antes do bloqueio e ``travou``.
    """

    buffer: list[object] = [None] * TAMANHO_BUFFER
    recebidas: list[object] = []
    vazio = threading.Semaphore(TAMANHO_BUFFER)
    cheio = threading.Semaphore(0)
    mutex = threading.Semaphore(1)
    estado = {"escrita": 0, "leitura": 0}
    travou = False

    def produtor() -> None:
        """Adquire mutex antes de vazio, reproduzindo a ordem problemática."""

        for amostra in range(total):
            mutex.acquire()
            vazio.acquire()
            indice = estado["escrita"]
            buffer[indice] = amostra
            estado["escrita"] = (indice + 1) % TAMANHO_BUFFER
            mutex.release()
            cheio.release()

    def consumidor() -> None:
        """Tenta retirar itens e encerra se passar um segundo sem progresso."""

        nonlocal travou
        for _ in range(total):
            if not cheio.acquire(timeout=TIMEOUT_SEGUNDOS):
                travou = True
                return
            if not mutex.acquire(timeout=TIMEOUT_SEGUNDOS):
                travou = True
                return
            indice = estado["leitura"]
            recebidas.append(buffer[indice])
            buffer[indice] = None
            estado["leitura"] = (indice + 1) % TAMANHO_BUFFER
            mutex.release()
            vazio.release()

    thread_produtor = threading.Thread(target=produtor, name="sensor", daemon=True)
    thread_consumidor = threading.Thread(target=consumidor, name="motor")
    thread_produtor.start()
    thread_consumidor.start()
    thread_consumidor.join(timeout=TIMEOUT_SEGUNDOS + 1.0)
    if thread_consumidor.is_alive():
        travou = True
    return recebidas, travou


def ler_argumentos() -> argparse.Namespace:
    """Lê e valida a quantidade opcional de amostras.

    Returns:
        Namespace com ``amostras`` inteiro e positivo.
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
    imprimir_resultado("Versão 3 — ordem trocada", args.amostras, metricas)

