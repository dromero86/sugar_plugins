PLUGINS_DIR := $(HOME)/.sugar/plugins
SRC_DIR := $(CURDIR)/src
PY_VERSION := $(shell python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
DEPS_DIR := $(HOME)/.sugar/site-packages-py$(PY_VERSION)
PIP := python3 -m pip

.PHONY: all install install-system-deps install-ai-native symlinks

all: install symlinks

# Cada plugin puede declarar en src/<plugin>/apt-requirements.txt
# (opcional) los paquetes de sistema (headers/librerias de desarrollo)
# que necesita para compilar sus dependencias Python nativas. Un
# requisito por linea, '#' para comentarios. Cuando el nombre de
# paquete cambia entre versiones de Debian (ej. libmysqlclient-dev en
# bullseye vs default-libmysqlclient-dev en versiones mas nuevas),
# listar las alternativas en la misma linea separadas por "|" SIN
# espacios (ej. "libmysqlclient-dev|default-libmysqlclient-dev"): se
# instala la primera que exista en el cache de apt de esta maquina, y
# si alguna alternativa ya esta instalada no se hace nada.
#
# Junta los apt-requirements.txt de TODOS los plugins, resuelve cada
# requisito contra el apt de esta maquina (no contra una lista fija de
# nombres), e instala solo lo que falte. Pide privilegios de sudo
# interactivamente si hacen falta; si `apt-get` no esta disponible
# (sistema no basado en Debian) o ninguna alternativa de un requisito
# existe en el cache de esta maquina, avisa y sigue sin fallar el
# build por eso.
install-system-deps:
	@if ! command -v apt-get >/dev/null 2>&1; then \
		echo "aviso: apt-get no disponible, omitiendo instalacion de dependencias de sistema"; \
		exit 0; \
	fi; \
	tmp=$$(mktemp); \
	cat $(SRC_DIR)/*/apt-requirements.txt 2>/dev/null | sed 's/#.*//' | sed '/^[[:space:]]*$$/d' | sort -u > "$$tmp"; \
	missing=""; \
	unresolved=""; \
	while IFS= read -r req; do \
		old_ifs=$$IFS; IFS='|'; set -- $$req; IFS=$$old_ifs; \
		satisfied=0; \
		for alt in "$$@"; do \
			if dpkg -s "$$alt" >/dev/null 2>&1; then satisfied=1; break; fi; \
		done; \
		if [ "$$satisfied" = 0 ]; then \
			chosen=""; \
			for alt in "$$@"; do \
				if apt-cache show "$$alt" 2>/dev/null | grep -q '^Package:'; then chosen="$$alt"; break; fi; \
			done; \
			if [ -n "$$chosen" ]; then \
				missing="$$missing $$chosen"; \
			else \
				unresolved="$$unresolved $$req"; \
			fi; \
		fi; \
	done < "$$tmp"; \
	rm -f "$$tmp"; \
	if [ -n "$$unresolved" ]; then \
		echo "aviso: ningun paquete apt disponible en esta maquina para:$$unresolved (instalalo manualmente si el plugin correspondiente falla)"; \
	fi; \
	if [ -n "$$missing" ]; then \
		echo "Instalando dependencias de sistema faltantes:$$missing"; \
		sudo apt-get update && sudo apt-get install -y $$missing; \
	else \
		echo "Dependencias de sistema de plugins: OK"; \
	fi

# Instala las dependencias de todos los plugins en un site-packages
# compartido y namespaceado por version de Python
# ($(DEPS_DIR)), que el binario `sugar` (PluginManager) agrega a
# sys.path automaticamente. `pip install --target` no toca el Python
# del sistema, asi que no dispara el bloqueo PEP 668
# (externally-managed-environment) de Debian 12+ ni requiere venv en
# Debian 11 / Python 3.9. El plugin ai_native queda fuera por defecto
# por sus dependencias pesadas (torch, transformers, ...); usa
# `make install-ai-native` para instalarlas aparte.
install: install-system-deps
	@mkdir -p $(DEPS_DIR)
	$(PIP) install --target $(DEPS_DIR) -r requirements.txt
	@for req in $(SRC_DIR)/*/requirements.txt; do \
		plugin=$$(basename $$(dirname $$req)); \
		if [ "$$plugin" = "ai_native" ]; then continue; fi; \
		echo "== $$plugin =="; \
		$(PIP) install --target $(DEPS_DIR) -r "$$req"; \
	done

install-ai-native:
	$(PIP) install -r $(SRC_DIR)/ai_native/requirements.txt

# Crea en $(PLUGINS_DIR) un enlace simbolico por cada plugin (carpeta
# de src/ con plugin.json) que aun no este enlazado.
symlinks:
	@mkdir -p $(PLUGINS_DIR)
	@for d in $(SRC_DIR)/*/; do \
		name=$$(basename "$$d"); \
		if [ -f "$${d}plugin.json" ]; then \
			link="$(PLUGINS_DIR)/$$name"; \
			if [ -e "$$link" ] || [ -L "$$link" ]; then \
				echo "skip (exists): $$name"; \
			else \
				ln -s "$${d%/}" "$$link"; \
				echo "linked: $$name"; \
			fi; \
		fi; \
	done
