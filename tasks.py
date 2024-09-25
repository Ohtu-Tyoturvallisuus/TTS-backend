""" tasks.py """
# pylint:   disable-all

import sys
from invoke.tasks import task

@task
def migrate(ctx):
    ctx.run("python3 manage.py migrate")

@task
def server(ctx):
    ctx.run("python3 manage.py runserver 0.0.0.0:8000")

@task
def lint(ctx):
    ctx.run("pylint .", warn=True)

@task
def unittest(ctx):
    ctx.run("pytest ./api/tests/unit")

@task
def coverage(ctx):
    ctx.run("pytest --cov=api --cov-report=html:docs/coverage --cov-report=term-missing ./api/tests/unit")

@task(coverage)
def coverage_report(ctx):
    print("Coverage report generated in HTML format in the docs/coverage directory. Check the htmlcov directory.")
