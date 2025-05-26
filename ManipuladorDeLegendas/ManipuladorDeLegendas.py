#!/usr/bin/python3

import argparse
import sys
import os
import re

def limpar_tela():
    """
    Função para limpar a tela do console executando que verifica se é windows para usar cls, 
    caso contrario usa clear que é funcional em qualquer *nix
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def step1(srcvtt):
    """
    Lógica para a execução da Etapa 1: Tradução do arquivo VTT original.
    """
    #Definição das variaveis da etapa:
    legenda_original = "legenda_original.txt"
    legenda_traduzida = "legenda_traduzida.txt"
    # Expressões regulares para identificar UUIDs e timestamps
    UUID_RE = re.compile(r'^[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}-\d+$')
    TIMESTAMP_RE = re.compile(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}$')

    print(f"[STEP 1] Iniciando processamento do VTT: {srcvtt}")
    
    #Valida se o VTT existe antes de prosseguir
    if not os.path.exists(srcvtt):
        print("[ERRO] O arquivo fornecido não foi encontrado.")
        return
    print(f"[INFO] Arquivo {srcvtt} carregado com sucesso, processando...")
    
    #Inicia o processamento do arquivo
    with open(srcvtt, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        
    #Cria uma lista vazia para funcionar com buffer final que será o conteúdo do arquivo
    #e define o indice de processamento de linhas como 0
    output = []
    i = 0
    
    # Verifica e remove cabeçalho WEBVTT (se presente)
    if lines and lines[0].strip().upper() == "WEBVTT":
        i += 1  # ignora a linha "WEBVTT"

    # Percorre todas as linhas do arquivo
    while i < len(lines):
        line = lines[i].strip()

        # Detecta início de bloco com UUID
        if UUID_RE.match(line):
            i += 1  # avança para o timestamp
            if i < len(lines) and TIMESTAMP_RE.match(lines[i].strip()):
                i += 1  # avança para as linhas de texto
            else:
                continue  # bloco inválido, pula
            
            #Define um uma lista vazia para ser usado como um buffer temporario do bloco de legendas 
            #a ser tratado até encontrar o proximo UUID, deixando tudo em uma unica linha por bloco.
            buffer = []
            # Coleta todas as linhas de texto até o próximo UUID ou linha em branco
            while i < len(lines) and lines[i].strip() != "" and not UUID_RE.match(lines[i].strip()):
                buffer.append(lines[i].strip())
                i += 1

            # Junta todas as linhas de texto em uma só, separadas por espaço
            if buffer:
                output.append(" ".join(buffer))

        else:
            # Ignora linhas fora do padrão
            i += 1
    #Ao fim do processamento do arquivo, Informa o sucesso da criação do arquivo de legenda original
    print(f"[INFO] Arquivo {srcvtt} processado.")

    #escreve o novo arquivo com uma linha por bloco de legenda
    print(f"[INFO] Criando arquivo {legenda_original} para ser usado de referencia para tradução!")
    with open(legenda_original, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    # Prepara o arquivo de tradução que será o input para a proxima etapa do script
    conteudo = """ATENÇÃO
=======
Utilize o arquivo legenda_original.txt como referencia para a tradução, e insira a versão traduzida
neste arquivo, respeitando sua sequencia de linhas.
Mesmo que logicamente uma frase faça mais sentido estar junta, pense nela como uma frase maior e 
segmente na mesma quantidade de linhas que se encontra na legenda original, caso contrario terá muito 
trabalho para ressincronizar a legenda.
O resultado esperado é ter um arquivo de legendas traduzidas com a mesma quantidade de linhas da 
legenda original.

Não se esqueça de eliminar este conteúdo antes de iniciar o processo de tradução neste arquivo!
"""

    # Abre o arquivo no modo de escrita ('w'), cria se não existir e sobrescreve se já existir
    print(f"[INFO] Criando arquivo {legenda_traduzida} para ser usado como referencia traduzida!")
    with open(legenda_traduzida, "w", encoding="utf-8") as f:
        f.write(conteudo)

    # Mensagem opcional de confirmação
    print(f"""\033[92m
[INFO] Utilize o arquivo {legenda_original} para usar de referencia para sua tradução,
Insira sua tradução no arquivo {legenda_traduzida} respeitando as informações contidas neste arquivo.
Não se esqueça de limpar as informações antes de iniciar a inserção das traduções.
Antes de executar a proxima etapa, sugiro validar se a quantidade de linhas em ambos os arquivos são iguais
Caso contrário, você sofrerá com a sincronização da legenda no vídeo.
\033[0m""")


def step2(dstvtt):
    """
    Lógica para a execução da Etapa 2: Validação ou pós-processamento do VTT traduzido.
    """
    print(f"[STEP 2] Executando Step 2 com o arquivo traduzido: {dstvtt}")
    # Aqui você poderá inserir sua lógica para validar ou ajustar o VTT traduzido
    if not os.path.exists(dstvtt):
        print("[ERRO] O arquivo fornecido não foi encontrado.")
        return
    print(f"[INFO] Arquivo {dstvtt} carregado com sucesso.")
    # ... processa VTT traduzido ...

def ask_for_step():
    """
    Exibe um menu interativo quando o usuário não fornece parâmetros na linha de comando.
    """
    limpar_tela()
    print("=== PROVA DE CONCEITO: PROCESSAMENTO DE VTT ===")
    print("Este script possui duas etapas possíveis:")
    print(" - Step 1: Fornece um arquivo .vtt original e executa a lógica de tradução.")
    print(" - Step 2: Fornece um arquivo .vtt traduzido e executa a validação/pós-processamento.")
    while True:
        step = input("Digite o número da etapa que deseja executar (1 ou 2): ").strip()
        if step == '1':
            limpar_tela()
            print("[INFO] Etapa 1 selecionada. Espera-se um arquivo VTT original para tradução.")
            srcvtt = input("Informe o caminho do arquivo .vtt original: ").strip()
            step1(srcvtt)
            break
        elif step == '2':
            limpar_tela()
            print("[INFO] Etapa 2 selecionada. Espera-se um arquivo VTT já traduzido.")
            dstvtt = input("Informe o caminho do arquivo .vtt traduzido: ").strip()
            step2(dstvtt)
            break
        else:
            print("[ERRO] Opção inválida. Digite apenas 1 ou 2.")

def main():
    """
    Função principal do script, responsável por analisar argumentos da linha de comando.
    O argparse cria o help que pode ser invocado com -h ou --help (pois não declaramos para ele não o fazer)
    """
    parser = argparse.ArgumentParser(description="Script para processar arquivos VTT em duas etapas.")
    
    # Cada argumento espera apenas um caminho de arquivo como valor
    parser.add_argument('--step1', help='Executa a Etapa 1 com um arquivo VTT original.')
    parser.add_argument('--step2', help='Executa a Etapa 2 com um arquivo VTT traduzido.')
    
    args = parser.parse_args()

    # Verifica se algum argumento foi passado
    if args.step1:
        step1(args.step1)
    elif args.step2:
        step2(args.step2)
    else:
        # Nenhum argumento? Inicia modo interativo
        ask_for_step()

# Garante que o script só será executado se for chamado diretamente
if __name__ == '__main__':
    main()
