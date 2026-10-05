# Plugin Ncurses para Sugar

Interfaces de terminal (TUI) para Sugar, con un **modelo de componentes estilo
Webix**: cada vista se declara con `{"ncurses": {"operator": "<view>", ...}}` y
el plugin resuelve todo en memoria (frontend puro, **no accede a datos**).

## Modelo

```json
{
  "ncurses": {
    "operator": "datatable",
    "data": "movies",
    "columns": [
      { "id": "nombre", "header": "Nombre", "fillspace": true, "sort": "string" },
      { "id": "imdb", "header": "Rating", "width": 8, "sort": "number", "format": "%.1f" }
    ],
    "select": "row",
    "id": "sel"
  }
}
```

- **`operator`**: la vista (`datatable`, `list`, `form`, `layout`, ...).
- **`data`**: filas del componente (lista inline o **nombre de variable Sugar**).
  `source` sigue aceptandose como alias legacy.
- **`id`**: binea el resultado en una variable de Sugar.
- **`template`**: placeholders `#campo#` (y `{campo}` por compatibilidad).
- **`events`**: handlers de eventos; acciones built-in
  (`detail`/`toggle`/`select`/`set`/`emit`/`close`/`none`/`navigate`/`back`) o
  una **funcion anonima inline** (`{"function": {...}}` / `{"lambda": {...}}`).
  Las funciones anonimas se ejecutan via el bridge plugin->Sugar (solo
  predicado/transformador; nunca abren otra vista).

Contrato de retorno: `{"status": "ok", "selected": ..., "values": ...,
"action": ..., "query": ...}` segun el componente.

## Componentes

- **Data**: `datatable`, `list`, `property`, `grouplist`, `dataview`,
  `unitlist`, `timeline`, `tree`, `pager`.
- **Controles**: `button`, `text`, `textarea`, `search`, `checkbox`, `radio`,
  `toggle`/`switch`, `counter`, `slider`, `rangeslider`, `select`,
  `richselect`, `combo`, `suggest`.
- **Estaticos**: `template`, `label`, `spacer`, `icon`.
- **Layout / contenedores**: `layout`, `window`, `popup`, `tooltip`,
  `context`, `multiview`, `carousel`, `tabbar`, `tabview`, `proxy`,
  `scrollview`, `align`, `abslayout`, `gridlayout`, `headerlayout`, `portlet`,
  `dashboard`, `accordion`.
- **Navegacion**: `menu`, `contextmenu`, `sidebar`, `toolbar`, `hint`.
- **Formularios**: `form`.
- **Vistas compuestas**: `composite`, `listview`, `formview`, `datafull`,
  `cardview`.
- **Visualizacion**: `gage`, `bullet`, `chart`.

## Contrato de componente

Un componente implementa `draw(window, region)` + `handle_key(key)` +
`result()`; el driver (`kernel/app.App`) corre el loop de pantalla. Un
`layout` compone hijos por region y **rutea las teclas al hijo enfocado**
(`Tab`/`Shift-Tab` cambia el foco). Los hijos interactivos (`datatable`,
`list`, `tree`, `form`) no corren su propio loop cuando estan compuestos.

## Ejemplo: layout lista + detalle

```json
{
  "ncurses": {
    "operator": "layout",
    "cols": [
      { "operator": "list", "data": "clientes", "template": "#nombre#", "width": 30, "id": "sel" },
      { "operator": "property", "data": "cliente_actual" }
    ]
  }
}
```

## Legacy

La API imperativa anterior (`init`, `create_window`, `create_button`, ...)
sigue disponible pero es **legacy**; el modelo de componentes la reemplaza.
Los operadores `not_implemented` se retiraron.

## Tests

```bash
cd src/ncurses && python3 -m pytest tests/ -q
```

No requieren terminal (stubean `curses`/`PluginBase`). Para correr en un
terminal real: `sugar -f examples/basic_usage.json`.
