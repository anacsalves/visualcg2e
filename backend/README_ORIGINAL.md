# Código do gerador original

Os módulos em `app/generators/convencional` e `app/generators/pwl` foram copiados do projeto enviado **Graph-Generator**.

As únicas alterações estruturais feitas nos arquivos centrais foram a troca dos imports absolutos por imports relativos, para que eles funcionem como pacotes dentro da API. A lógica de geração foi mantida.

A integração web, validação HTTP, conversão para JSON, atribuição opcional de pesos e montagem das respostas estão em `app/services.py`.

Licença original: MIT, preservada no arquivo `LICENSE` da raiz.
