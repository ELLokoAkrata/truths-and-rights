# Truths and Rights — Tareas comunes

.PHONY: build validate scrape check-emergency clean help

help: ## Mostrar esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construir base de datos para todos los países
	python3 scripts/build_db.py

build-pe: ## Construir base de datos solo para Perú
	python3 scripts/build_db.py --country PE

validate: ## Validar todos los datos
	python3 scripts/validate_sources.py

validate-pe: ## Validar datos de Perú
	python3 scripts/validate_sources.py --country PE

scrape: ## Scraping de fuentes oficiales
	python3 scripts/scrape_official.py --all

check-emergency: ## Verificar estados de emergencia vigentes
	python3 scripts/scrape_official.py --check-emergency

check-updates: ## Verificar si hay actualizaciones en fuentes
	python3 scripts/scrape_official.py --check-updates

test: build-pe ## Correr todos los tests con pytest
	python -m pytest tests/ -v

clean: ## Limpiar archivos generados
	rm -rf build/
	rm -rf data/PE/sources/raw/

stats: ## Mostrar estadísticas del proyecto
	@echo "=== Truths and Rights — Stats ==="
	@echo "Fuentes legales:" && find data/PE/sources -name "*.json" ! -path "*/raw/*" -exec cat {} \; | python3 -c "import sys,json; data=[]; [data.extend(json.load(open(f.strip()))) for f in sys.stdin if f.strip()]; print(f'  (ver validador)')" 2>/dev/null || echo "  Usar: make validate"
	@echo "Build:" && ls -lh build/truths_and_rights_pe.db 2>/dev/null || echo "  No existe. Correr: make build-pe"
