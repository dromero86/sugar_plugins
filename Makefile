PLUGINS_DIR := $(HOME)/.sugar/plugins
SRC_DIR := $(CURDIR)/src
PIP := python3 -m pip

.PHONY: all install install-ai-native symlinks

all: install symlinks

# Instala (a nivel de usuario, sin sudo) las dependencias de todos los
# plugins. El plugin ai_native queda fuera por defecto por sus
# dependencias pesadas (torch, transformers, ...); usa
# `make install-ai-native` para instalarlas aparte.
install:
	$(PIP) install -r requirements.txt
	@for req in $(SRC_DIR)/*/requirements.txt; do \
		plugin=$$(basename $$(dirname $$req)); \
		if [ "$$plugin" = "ai_native" ]; then continue; fi; \
		echo "== $$plugin =="; \
		$(PIP) install -r "$$req"; \
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
