# Variavel global usada para auxiliar no reconhecimento de uma palavra reservada
RESERVED_WORDS = ['NUMERO', 'CADEIA', 'BLOCO', 'FIM', 'PRINT']

import chardet

# Inicio do código
def main():

    # Insira aqui o nome do arquivo que será testado
    nome_do_arquivo = 'arq.txt'
    encoding_type = ""

    try:
        with open(nome_do_arquivo, "rb") as file:
            result = chardet.detect(file.read())
            encoding_type = result['encoding']

    except FileNotFoundError:
        print(f"Não foi possível abrir o arquivo '{nome_do_arquivo}', verifique se o arquivo existe no diretório.")
        return
    
    # Gera os tokens da linguagem (Assumindo que não haverá erro léxico)
    tokens = gerar_tokens(nome_do_arquivo, encoding_type)

    # Realiza a analise semantica e o gerenciamento de escopo.
    gerenciar_escopo(tokens)


# Processa o código do arquivo recebido e retorna a lista de todos os tokens reconhecidos
# No formato {token:nome_do_token, lexema:lexema_do_token}
def gerar_tokens(arq, encoding_type) -> list:

    tokens = []

    with open(arq, "r", encoding = encoding_type) as file:
        while True:
            tkn = next_token(file)

            if not tkn:
                print('Tokens reconhecidos com sucesso.\n')
                break

            tokens.append(tkn)

    return tokens
            
# Faz o gerenciamento de escopo juntamente com a analise semantica
# Verificando os tipos nas atribuições 
def gerenciar_escopo(tokens):
    pilha = []
    i = 0

    print('Inicio da analise semantica.\n')
    while True:
        if i == len(tokens): break

        # Se encontrou bloco, empilha uma tabela juntamente com seu id (Abriu novo escopo)
        if tokens[i]['token'] == 'tk_BLOCO':
            i += 1
            tabela = {"bloco":tokens[i]['lexema']}
            pilha.append(tabela)
        
        # Se encontrou fim, desempilha a tabela. (Fechou escopo atual)
        elif tokens[i]['token'] == 'tk_FIM':
            i += 1
            pilha.pop()

        # Encontrou um TIPO, logo, será feito uma ou mais atribuições.
        elif tokens[i]['token'] == 'tk_NUMERO' or tokens[i]['token'] == 'tk_CADEIA':
            
            # Salva o tipo e 'j' é o próximo token.
            tipo = tokens[i]['token'][3:].lower()
            j = i + 1

            # Sai do loop quando encontrado um token que não seja virgula, identificador ou atribuição.
            while True:
                
                # Encontrou um identificador
                if tokens[j]['token'] == 'tk_identificador':
                    
                    # Tratamento para atribuição
                    if tokens[j+1]['token'] == 'tk_atr':
                        
                        # Verifica se o identificador foi declarado no escopo atual
                        valor = busca_no_escopo(pilha[-1], tokens[j]['lexema'])

                        # Se não foi declarado, adiciona na tabela.
                        if not valor:
                            pilha[-1].update({tokens[j]['lexema']:{"tipo":tipo, "valor":tokens[j+2]['lexema']}})
                            j += 2
                        
                        # Se o identificador já foi declarado no escopo
                        else:
                            #print(pilha[-1])
                            if pilha[-1][tokens[j]['lexema']]['tipo'] != tipo.lower():
                                print(f"Erro 1: Tipos nao compativeis - falha ao atribuir {pilha[-1][tokens[j]['lexema']]['tipo']} e {tipo.lower()}.")
                            
                            else:
                                pilha[-1][tokens[j]['lexema']].update({'tipo':tipo, "valor":tokens[j+2]['lexema']})
                            
                            j += 2

                elif tokens[j]['token'] == 'tk_virg':
                    j += 1
                    continue

                # Leu token diferente de atribuição, virgula ou identificador, decrementa o índice ('deslendo' ele) e sai do loop.
                else:
                    j -= 1
                    i = j
                    break

                j += 1

        # Encontrou comando de print
        elif tokens[i]['token'] == 'tk_PRINT':
            i += 1

            declarado = False

            # Busca identificador do escopo atual até o mais externo.
            for k in range(len(pilha)-1, -1, -1):
                valor = busca_no_escopo(pilha[k], tokens[i]['lexema'])

                if valor:
                    declarado = True
                    break
            
            # Se não encontrou, a variável não foi declarada, portanto é erro.
            if not declarado:
                print(f"Erro 2: Variavel nao declarada - variavel {tokens[i]['lexema']} nao existe no escopo do bloco {pilha[-1]['bloco']}.")

            # Imprime o valor do identificador no bloco atual.
            else:
                print(f"{tokens[i]['lexema']} -> {valor} (Bloco {pilha[-1]['bloco']}).")


        # Se está lendo um identificador, será uma atribuição
        elif tokens[i]['token'] == 'tk_identificador':
            
            # Busca o identificador no escopo atual
            valor = busca_no_escopo(pilha[-1], tokens[i]['lexema'])

            # Se o identificador não foi encontrado no escopo atual
            if not valor:
                j = i
                i += 2

                # Se for atribuição do tipo id = CONST Ele é declarado com o tipo inferido na atribuição.

                if tokens[i]['token'] == 'tk_cadeia':
                        pilha[-1].update({tokens[j]['lexema']:{'tipo':'cadeia', 'valor':tokens[i]['lexema']}})

                elif tokens[i]['token'] == 'tk_numero':
                        pilha[-1].update({tokens[j]['lexema']:{'tipo':'numero', 'valor':tokens[i]['lexema']}})

                # Se for atribuição do tipo id = id, busca o valor do id que será atribuído
                else:

                    for k in range(len(pilha)-1, -1, -1):
                        valor = busca_no_escopo(pilha[k], tokens[i]['lexema'])
                        if valor: break

                    if valor:
                        pilha[-1].update({tokens[j]['lexema']:{'tipo':tokens[i]['token'][3:], 'valor':valor}})
                    else:
                        print('Falha ao tentar atribuir uma variavel inexistente')

            # Identificador já foi declarado no escopo
            else:
                j = i
                i += 2

                # Entra no if se for atribuição do tipo id = const
                if tokens[i]['token'] != 'tk_identificador':

                    # Verifica se os tipos são iguais e realiza a atribuição
                    if pilha[-1][tokens[j]['lexema']]['tipo'] == tokens[i]['token'][3:]:
                        pilha[-1].update({tokens[j]['lexema']:{'valor':tokens[i]['lexema']}})

                    else:
                        print(f"Erro 1: Tipos nao compativeis - falha ao atribuir {pilha[-1][tokens[j]['lexema']]['tipo']} e {tokens[i]['token'][3:]}.")

                else:        
                    # Atribuição do tipo id = id
                    declarado = False

                    # Busca o valor do id que será atribuído
                    for k in range(len(pilha)-1, -1, -1):
                        valor = busca_no_escopo(pilha[k], tokens[i]['lexema'])

                        if valor:
                            declarado = True
                            escopo2 = k
                            break

                    if not declarado:
                        print('Falha ao tentar atribuir uma variavel inexistente')
                    
                    # Se os dois identificadores existem
                    else:

                        # Exibe erro se os tipos não forem compatíveis, caso sejam, realiza a atribuição.
                        if pilha[-1][tokens[j]['lexema']]['tipo'] != pilha[escopo2][tokens[i]['lexema']]['tipo']:
                            print(f"Erro 1: Tipos nao compativeis - falha ao atribuir {pilha[-1][tokens[j]['lexema']]['tipo']} e {pilha[escopo2][tokens[i]['lexema']]['tipo']}.")

                        else:
                            pilha[-1][tokens[i]['lexema']].update({'valor':pilha[escopo2][tokens[i]['lexema']]['valor']})
        i += 1
    
    print('\nFim da analise semantica.')


# Procura uma variável dentro do escopo recebido e retorna o valor dela caso exista
def busca_no_escopo(tabela: dict, variavel: str):
    try:
        conteudo = tabela.get(variavel)
        valor = conteudo['valor']
        return valor
    
    except (TypeError, KeyError):
        return False

# ====================================================================== #
# A parte abaixo é correspondente ao analisador léxico, responsável por
# retornar os tokens da linguagem fornecida no arquivo de entrada.

def read_char(file):
    return file.read(1)

def unread_char(file):
    file.seek(file.tell()-1)
     
def is_reserved_word(word):

    if word not in RESERVED_WORDS:
        return False
    
    return {"token":"tk_"+word, "lexema":word}

def next_token(file):
    lexema = ''
    state = 0

    while True:
        char = read_char(file)

        if char == "": return False

        match state:
            case 0:
                if char in '\n ':
                    state = 0
                    continue

                elif char in '+-':
                    state = 1

                elif char.isdigit():
                    state = 2
                
                elif char == "\"":
                    state = 5

                elif char.isupper():
                    state = 7

                elif char.islower():
                    state = 8

                elif char == '_':
                    state = 9

                elif char == '=':
                    state = 12
                
                elif char == ',':
                    state = 13

                else: return False
                
                lexema += char

            case 1:
                if char.isdigit():
                    lexema += char
                    state = 2

            case 2:
                if char.isdigit():
                    lexema += char
                    state = 2

                elif char == '.':
                    lexema += char
                    state = 3
                
                else:
                    unread_char(file)
                    return {"token":"tk_numero", "lexema":lexema}

            case 3:
                if char.isdigit():
                    lexema += char
                    state = 4

            case 4:
                if char.isdigit():
                    lexema += char
                    state = 4

                else:
                    unread_char(file)
                    return {"token":"tk_numero", "lexema":lexema}
                
            case 5:
                if char == '"':
                    lexema += char
                    state = 6
                
                else:
                    lexema += char

            case 6:
                unread_char(file)
                return {"token":"tk_cadeia", "lexema":lexema}
            
            case 7:
                if char.isupper():
                    lexema += char
                    state = 7
                
                else:
                    unread_char(file)
                    return is_reserved_word(lexema)
                
            case 8:
                if char.isalnum() or char == '_':
                    lexema += char
                    state = 8
                
                else:
                    unread_char(file)
                    return {"token":"tk_identificador", "lexema":lexema}
                
            case 9:
                if char.isalnum():
                    lexema += char
                    state = 10


            case 10:
                if char.isalnum():
                    lexema += char
                    state = 10
                
                elif char == '_':
                    lexema += char
                    return {"token":"tk_id_bloco", "lexema":lexema}
            
            case 12:
                unread_char(file)
                return {"token":"tk_atr", "lexema":lexema}
            
            case 13:
                unread_char(file)
                return {"token":"tk_virg", "lexema":lexema}
            
if __name__ == '__main__':
    main()