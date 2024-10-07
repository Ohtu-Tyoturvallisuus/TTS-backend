""" tasks.py """
# pylint: disable-all

import sys
from invoke.tasks import task

@task
def migrate(ctx):
    if sys.platform.startswith("win"):
        ctx.run("py manage.py migrate")
    else:
        ctx.run("python3 manage.py migrate")

@task
def makemigrations(ctx):
    if sys.platform.startswith("win"):
        ctx.run("py manage.py makemigrations")
    else:
        ctx.run("python3 manage.py makemigrations")

@task
def server(ctx):
    if sys.platform.startswith("win"):
        ctx.run("py manage.py runserver 0.0.0.0:8000")
    else:
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

