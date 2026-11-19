.PHONY: lint-docs test-lint

lint-docs:
	python3 scripts/lint_docs.py .

test-lint:
	cd scripts && python3 -m unittest discover -p 'test_*.py' -v
