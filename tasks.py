from invoke import task
from pathlib import Path

PACKAGE = "mplchart"
ROOT = Path(__file__).parent


@task
def info(c):
    """ Publish to PyPI with twine """
    c.run(f"pip index versions {PACKAGE}")


@task
def clean(c):
    """ Clean project dist """
    c.run("rm -rf dist")


@task(clean)
def build(c):
    """ Build project wheel """
    c.run("nbfixme examples misc")
    c.run("python -mbuild --wheel")


@task
def dump(c):
    """ Dump wheel contents """
    for file in ROOT.glob("dist/*.whl"):
        c.run(f"unzip -l {file}")


@task
def publish(c):
    """ Publish to PyPI with twine """
    c.run("twine upload dist/*.whl")
