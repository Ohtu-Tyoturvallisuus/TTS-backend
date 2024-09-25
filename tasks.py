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
