.PHONY: upgrade test docs

upgrade: ## update python dependencies
	uv run --with edx-lint edx_lint write_uv_constraints pyproject.toml
	uv lock --upgrade

test: ## run unit tests with coverage
	cd testproject && pytest --cov wiki --cov django_notify

docs: ## build HTML documentation
	make -C docs html
