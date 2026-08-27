# Visual CG2E

Interface web para geração e visualização de grafos integrada ao gerador CG2E em Python.

O projeto mantém a lógica de geração concentrada no backend e utiliza o frontend apenas para entrada de parâmetros, apresentação dos resultados e exportação dos datasets gerados.

## Execução no Windows

Na pasta raiz do projeto, execute:

```bat
run-backend.bat
```

Na primeira execução, o script:

1. cria o ambiente virtual em `backend/.venv`;
2. instala as dependências Python;
3. verifica a disponibilidade do `python-igraph`;
4. tenta instalar `pycairo` e, se necessário, `cairocffi` para a renderização dos grafos;
5. inicia a API e serve o frontend compilado.

Depois, abra no navegador:

```text
http://localhost:8000
```

A documentação interativa da API fica disponível em:

```text
http://localhost:8000/docs
```

> **Importante:** não copie a pasta `backend/.venv` entre diretórios ou computadores. Se o projeto for movido ou copiado para outro local e apresentar problemas de dependências, apague `backend/.venv` e execute novamente `run-backend.bat`.

## Estrutura do projeto

```text
Visual-CG2E/
├── backend/
│   ├── app/
│   │   ├── generators/
│   │   │   ├── convencional/   gerador convencional CG2E
│   │   │   └── pwl/            gerador power-law
│   │   ├── main.py              aplicação FastAPI e rotas
│   │   ├── schemas.py           validação dos parâmetros
│   │   └── services.py          integração entre API e geradores
│   ├── generated_images/        imagens produzidas pelo backend
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/                     código-fonte TypeScript/CSS
│   └── dist/                    frontend compilado
├── run-backend.bat
├── run-frontend.bat
├── run-backend.sh
├── run-frontend.sh
├── README.md
└── LICENSE
```

## Funcionamento

O fluxo principal da aplicação é:

```text
Usuário
   ↓
Interface web
   ↓
API FastAPI
   ↓
Gerador CG2E
   ↓
Dados do grafo
   ↓
Renderização da imagem no backend
   ↓
Interface web
```

No modo convencional, a API chama diretamente a função `geraDataset(...)` do gerador CG2E. Dessa forma, a escolha das arestas e a estrutura matemática do grafo permanecem no gerador Python.

A interface não cria nem substitui as arestas do grafo. Ela envia os parâmetros ao backend e apresenta os dados retornados.

## Geração convencional

O gerador convencional permite trabalhar com os seguintes tipos:

- grafo simples;
- dígrafo;
- multigrafo;
- multigrafo dirigido;
- pseudógrafo;
- pseudógrafo dirigido.

Também são aceitos:

- número de vértices;
- número de componentes conexas;
- número de arestas;
- preferência de densidade;
- distribuição das componentes;
- grafos valorados;
- peso mínimo e máximo;
- semente;
- geração de múltiplos datasets.

O valor padrão de componentes conexas é **1**, representando um grafo conexo.

## Preferência de densidade

A interface oferece três opções:

- **Sem preferência**;
- **Esparso:** `d ≤ 0,2`;
- **Denso:** `d ≥ 0,8`.

A densidade é calculada em relação ao número máximo de arestas permitido para o tipo de grafo selecionado.


## Geração power-law

O projeto também integra o gerador power-law, com expoente `gamma` entre 2 e 3.

Essa opção permite gerar redes em que poucos vértices concentram muitas conexões enquanto a maioria possui grau menor.

## Visualização

Para os grafos convencionais, a imagem é gerada no backend utilizando `python-igraph` e o layout Kamada-Kawai.

A renderização depende de uma implementação Cairo disponível no ambiente Python:

- `pycairo`, preferencialmente; ou
- `cairocffi`, como alternativa de compatibilidade.

Se o `igraph` não conseguir renderizar a imagem, o backend informa o erro em vez de gerar uma representação visual diferente.

## Exportação

A interface permite exportar:

- a imagem do grafo em PNG;
- os dados do grafo em TXT;
- todos os PNGs de um conjunto de datasets;
- todos os TXT de um conjunto de datasets.

## Frontend

O frontend compilado já está disponível em `frontend/dist` e é servido pelo FastAPI. Portanto, Node.js não é necessário para apenas executar a versão pronta.

Para desenvolver ou alterar o frontend, execute em outro terminal:

```bat
run-frontend.bat
```

Ou manualmente:

```bash
cd frontend
npm install
npm run dev
```

Depois de alterações no código-fonte:

```bash
npm run build
```

## Execução manual do backend

```bash
cd backend
python -m venv .venv
```

No Windows:

```bat
.venv\Scripts\activate
```

No Linux ou macOS:

```bash
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

Para a renderização do `igraph`, instale também uma implementação Cairo caso ainda não esteja disponível:

```bash
python -m pip install pycairo
```

Se a instalação do `pycairo` não estiver disponível no ambiente:

```bash
python -m pip install cairocffi
```

Por fim:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

## Testes

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm run build
```

## Código original e integração web

O Visual CG2E utiliza como base o gerador de grafos CG2E, desenvolvido originalmente por Gustavo Paulino. O código original do projeto está disponível em seu repositório no GitHub: [[link do repositório](https://github.com/gustavoc5/Graph-Generator)].

A partir dessa base, foram desenvolvidas as adaptações necessárias para a integração com a aplicação web, incluindo a comunicação entre frontend e backend, validação dos parâmetros, visualização dos grafos gerados e recursos de exportação.

No gerador convencional, a API preserva a chamada ao motor CG2E por meio de `geraDataset(...)`. A camada web é responsável por validação de entrada, comunicação HTTP, organização dos resultados, disponibilização das imagens e exportação.

## Licença

Este projeto é distribuído sob a licença MIT. O aviso de copyright do código original foi preservado no arquivo [`LICENSE`](LICENSE).
