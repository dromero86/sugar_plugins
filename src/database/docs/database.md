# Base de Datos (Database)

Permite interactuar con bases de datos relacionales, abriendo y cerrando conexiones y ejecutando sentencias SQL.

## Palabra Reservada
`db`

## Parámetros
* dns (string, opcional): Cadena de conexión a la base de datos (Data Source Name). Puede ser una cadena explícita o una referencia a una variable de entorno ("env(DSN)").
* connection (string, opcional): Operación de conexión ("open" o "close").
* sql (string, opcional): Sentencia SQL a ejecutar. Puede incluir variables interpoladas ("{{value}}").
* value (string, opcional): Nombre de la variable donde se almacenará el resultado de una consulta SELECT. Si la consulta devuelve múltiples filas, se almacena como un array de diccionarios. Si es una sola fila, como un diccionario.

Para SELECT de una sola columna, puede ser el nombre de la variable de tipo string donde se almacena el valor de la columna especificada en store.

store (array of objects, opcional): Para consultas SELECT de una sola fila/columna, define cómo almacenar valores específicos en variables.

* column (string): Nombre de la columna a extraer.
* value (string): Nombre de la variable donde se almacenará el valor de la columna.
* engine (object, opcional): Permite capturar métricas de la ejecución SQL.
* name (string): Métrica a capturar ("affected_rows", "execution_time", "errors").
* value (string): Nombre de la variable donde se almacenará el valor de la métrica.

## Ejemplos de Uso

### Abrir conexión (explícita)
```json
{ "db": { "dns": "mariadb+mariadbconnector://root:root@localhost:3306/test" } }
```

### Abrir conexión (desde variable de entorno)
```json
{ "db": { "dns": "env(DSN)" } }
```

### Establecer conexión (después de definir dns)
```json
{ "db": { "connection": "open" } }
```

### Cerrar conexión
```json
{ "db": { "connection": "close" } }
```

### Consultar múltiples filas (resulta en array de diccionarios)
```json
{ "db": { "sql": "SELECT id, name FROM users", "value": "users_list"  } }
```

### Consultar una sola fila (resulta en un diccionario)
```json
{ "db": { "sql": "SELECT id, name FROM users WHERE id = 1", "value": "user_data"  } }
```

### Consultar una sola columna de una fila específica (resulta en un string)
```json
{ "db": { "sql": "SELECT email FROM users WHERE id = 1", "store": [{ "column":"email", "value":"user_email" }]  } }
```

### Actualizar datos (sin retorno, sin asignación)
```json
[
  { "let": { "name": "new_name", "value": "John Doe Updated" } },
  { "db": { "sql": "UPDATE users SET name = '{{new_name}}' WHERE id = 1"  } }
]
```

### Insertar datos (con interpolación de variables)
```json
[
  { "let": { "name": "new_user_name", "value": "Jane Smith" } },
  { "db": { "sql": "INSERT INTO users (name) VALUES ('{{new_user_name}}')"  } }
]
```

### Insertar datos (con valor dinámico, sin interpolación para prevenir inyección SQL si el motor de base de datos lo soporta)
```json
[
  { "let": { "name": "dynamic_value", "value": "Dynamic Content" } },
  { "db": { "sql": "INSERT INTO logs (message) VALUES ('${dynamic_value}')" } }
]
```

### Insertar datos y capturar filas afectadas
```json
[
  { "let": { "name": "product_name", "value": "New Product" } },
  {
    "db": {
      "sql": "INSERT INTO products (name) VALUES ('{{product_name}}')",
      "engine": {
        "name": "affected_rows",
        "value": "inserted_rows_count"
      }
    }
  },
  { "print": {"text": "Filas insertadas: {{inserted_rows_count}}"} }
]
```