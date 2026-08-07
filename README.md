# Visual CG2E — projeto completo

Projeto web integrado ao gerador de grafos enviado em `Graph-Generator.zip`.

## Execução mais simples no Windows

Execute:

```bat
run-backend.bat
```

O script cria o ambiente Python, instala as dependências e inicia o sistema. Depois, abra:

```text
http://localhost:8000
```

A documentação da API fica em:

```text
http://localhost:8000/docs
```

O frontend já está compilado em `frontend/dist` e é servido pelo próprio FastAPI. Portanto, não é necessário instalar Node.js apenas para executar a versão pronta.

## Estrutura

```text
visual-cg2e-completo/
├── backend/
│   ├── app/
│   │   ├── generators/      código central do gerador convencional e power-law
│   │   ├── main.py          rotas da API e entrega do frontend
│   │   ├── schemas.py       validação dos parâmetros
│   │   └── services.py      integração do gerador com JSON
│   └── tests/
├── frontend/
│   ├── src/                 código-fonte em TypeScript
│   └── dist/                frontend compilado e pronto para execução
├── run-backend.bat
├── run-frontend.bat         modo de desenvolvimento opcional
└── LICENSE
```

## Desenvolvimento do frontend

Para editar o TypeScript com Vite, mantenha o backend aberto e execute em outro terminal:

```bat
run-frontend.bat
```

O Vite normalmente abrirá `http://localhost:5173` e encaminhará as chamadas `/api` para o backend.

Depois de alterar o frontend:

```bash
cd frontend
npm install
npm run build
```

## Execução manual do backend

```bash
cd backend
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
```

Linux ou macOS:

```bash
source .venv/bin/activate
```

Em seguida:

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

## Recursos integrados

- Gerador convencional com os seis tipos de grafo.
- Número exato de componentes conexas, inclusive quando o valor é 1.
- Estratégias aleatória, parcialmente balanceada e balanceada.
- Limites de arestas calculados pelo backend.
- Gerador power-law com gamma entre 2 e 3.
- Pesos opcionais sem alterar a estrutura produzida pelo gerador.
- Múltiplos datasets e navegação entre eles.
- Visualização SVG de laços, setas e arestas múltiplas.
- Exportação em PNG, JSON, CSV e TXT.

A interface limita a visualização a 300 vértices para evitar travamentos no navegador. A API aceita até 5.000 vértices.

## Divisão de responsabilidades

O frontend não escolhe as arestas. Ele apenas:

1. envia os parâmetros à API;
2. recebe os vértices e as arestas em JSON;
3. calcula somente as posições visuais;
4. desenha e exporta o resultado.

A estrutura matemática dos grafos é produzida pelos módulos Python.

## Código original

Os módulos em `backend/app/generators` vieram do projeto enviado. Os imports foram ajustados para o formato de pacote Python. A integração web está separada em `backend/app/services.py`.

A licença MIT original foi preservada no arquivo `LICENSE`.

## Testes

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
tsc -p tsconfig.json
```

## Compatibilidade com o gerador convencional original

A API chama diretamente `geraDataset(...)`, mantendo o mesmo caminho de execução, a mesma semente, a mesma ordem das arestas e a mesma sequência de pesos do programa Python original.

A disposição visual pode não ser idêntica à imagem criada por `visualizacao.py`: o programa original usa o layout Kamada–Kawai do igraph, enquanto o navegador organiza os mesmos vértices e arestas com um layout SVG próprio.
