FROM python:3.13-slim

# para o poetry não criar ambientes virtuais
ENV POETRY_VIRTUALENVS_CREATE=false

# define o diretório de trabalho onde o código será copiado
WORKDIR app/

# copia os arquivos de código para o diretório de trabalho, os . . servem para copiar todos os arquivos do diretório atual
COPY . .

# instala o poetry no container
RUN pip install poetry

# esse comando acima é para aumentar o número de workers do poetry, assim ele instala as dependências mais rápido
RUN poetry config installer.max-workers 10 

# instala as dependências do projeto, sem interação e sem ANSI, o without dev é para não instalar as dependências de desenvolvimento
RUN poetry install --no-interaction --no-ansi --without dev

# define a porta que o container irá expor
EXPOSE 8000
