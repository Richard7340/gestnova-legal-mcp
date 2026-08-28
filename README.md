# gestnova-legal-mcp

Servidor **MCP** que le da a un agente conocimiento jurídico aplicado: normativa,
cumplimiento, contratos y laboral, con la fuente citada.

Está pensado para que un asistente no responda de memoria sobre leyes. Cada
respuesta se apoya en el texto que hay en la base, con su referencia y su fecha,
y el servidor avisa cuando una norma lleva demasiado tiempo sin revisarse en
lugar de darla por buena.

## Qué expone

| Área | Para qué sirve |
|---|---|
| `legislation` | Consulta de normativa por materia y jurisdicción |
| `compliance` | Obligaciones y comprobaciones de cumplimiento |
| `contracts` | Análisis de cláusulas y revisión de contratos |
| `labor` | Materia laboral |
| `query` | Búsqueda transversal sobre lo anterior |
| `meta` | Estado de la base: qué hay cargado y desde cuándo |

## Cómo se usa

Necesita Python 3.11+ y una base PostgreSQL donde vive el corpus.

```bash
uv sync                       # o: pip install -e .
export LEGAL_MCP_DSN="postgresql://usuario:clave@host:5432/legal"
python -m gestnova_legal.server        # modo stdio, el habitual en MCP
```

Y en la configuración de tu cliente MCP (Claude Desktop, Claude Code, etc.):

```json
{
  "mcpServers": {
    "legal": {
      "command": "python",
      "args": ["-m", "gestnova_legal.server"],
      "env": { "LEGAL_MCP_DSN": "postgresql://..." }
    }
  }
}
```

Trae también un servidor HTTP (`http_server.py`) para cuando el cliente prefiere
conector remoto en vez de stdio.

## Sobre el contenido jurídico

El código es abierto; **el corpus no viene incluido**. Cada quien carga la
normativa que necesita con las herramientas de `seed`. Eso es deliberado: la
utilidad de un asistente legal depende de que su fuente esté actualizada y sea
la de tu jurisdicción, y eso no se puede empaquetar y olvidar.

Nada de lo que devuelve es asesoramiento legal.

## Tests

```bash
pytest
```

## Licencia

MIT. Úsalo, modifícalo y véndelo si te sirve. Si te resulta útil, nos alegra
saberlo: [gestnova.eu](https://gestnova.eu)
