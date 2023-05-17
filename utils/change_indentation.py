import sys

# Verifica se o nome do arquivo de entrada foi passado como argumento
if len(sys.argv) < 2:
    print("Usage: python change_indentation.py input_file.py")
    sys.exit()

# Abre o arquivo de entrada para leitura
with open(sys.argv[1], "r") as file:
    lines = file.readlines()

# Abre o arquivo de entrada para escrita
with open(sys.argv[1], "w") as file:
    for line in lines:
        # Substitui todas as ocorrências de 2 espaços por 4 espaços
        line = line.replace("  ", "    ")
        file.write(line)

