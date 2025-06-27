PACKAGE_NAME = multistamper

.PHONY: help build install uninstall clean publish

help:
	@echo "Usage:"
	@echo "  make build      - Build the wheel package"
	@echo "  make install    - Install the package locally"
	@echo "  make uninstall  - Uninstall the package and CLI binary"
	@echo "  make clean      - Remove build artifacts"
	@echo "  make publish    - Upload package to PyPI (requires twine)"

build:
	@echo "🔧 Building package..."
	python -m build

install:
	@echo "📦 Installing package locally..."
	pip install --upgrade dist/$(PACKAGE_NAME)-*.whl

uninstall:
	@echo "🗑️  Uninstalling package and CLI binary..."
	-pip uninstall -y $(PACKAGE_NAME)
	@bin_path=$$(which $(PACKAGE_NAME) 2>/dev/null); \
	if [ -n "$$bin_path" ]; then \
		echo "Removing CLI binary at $$bin_path"; \
		rm -f $$bin_path; \
	else \
		echo "CLI binary not found."; \
	fi

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/ dist/ *.egg-info

publish: build
	@echo "🚀 Publishing to PyPI..."
	twine upload dist/*
