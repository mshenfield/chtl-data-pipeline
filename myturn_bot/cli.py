import click
from enum import Enum

from .chtl import OPEN_YEARS
from .pipeline import pipeline as _pipeline, MyTurnFiles, Stages


class ListParam(click.ParamType):
    """Comma separated list of typed values."""

    name = "list"

    def __init__(self, element_class, converter=None):
        """Create a ListParam instance for a given class."""

        self.element_class = element_class
        # By default, just use the class constructor as the string->element_class converter.
        self.converter = element_class if converter is None else converter

    def convert(self, value, param, ctx):
        if isinstance(value, list) or (
            len(value) == 0 or isinstance(value[0], self.element_class)
        ):
            return value

        try:
            return [self.converter(v) for v in value.split(",")]
        except ValueError:
            self.fail(
                f"{value!r} must contain a comma separated list of {self.element_class} values",
                param,
                ctx,
            )


class EnumListParam(ListParam):
    """Comma separated list of enum values."""

    name = "enumlist"

    def __init__(self, enum_class):
        """Create an EnumListParm instance for a given Enum subclass."""

        if not issubclass(enum_class, Enum):
            raise ValueError(
                f"The enum_class parameter must be a subclass of Enum. Got '{enum_class}'"
            )
        super().__init__(enum_class, converter=lambda v: enum_class[v])


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--output",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, writable=True),
    help="The directory to place downloaded and processed data.",
)
@click.option(
    "--username",
    prompt=True,
    help="The username to access MyTurn with. If not provided it will prompt for a username.",
)
@click.option(
    "--password",
    prompt=True,
    hide_input=True,
    # TODO: CHTL specific
    help="The password to access MyTurn with. If not provided it will prompt for a password.",
)
@click.option(
    "--subdomain",
    # TODO: CHTL specific
    default="capitolhill",
    show_default=True,
    help="The myturn.com subdomain to download files from.",
)
@click.option(
    "--stages",
    type=EnumListParam(Stages),
    default=list(Stages),
    show_default=True,
    help=f"The stages of the pipeline to run.",
)
@click.option(
    "--files",
    type=EnumListParam(MyTurnFiles),
    default=list(MyTurnFiles),
    show_default=True,
    help=f"The files and reports to download and process.",
)
@click.option(
    "--years",
    type=ListParam(int),
    # TODO: This is very CHTL specific!
    default=OPEN_YEARS,
    help="A comma separated list of years to download loans and transactions for. By default, all "
    "the years CHTL has been officially open.",
)
def pipeline(output, subdomain, username, password, stages, files, years):
    _pipeline(
        output_dir=output,
        myturn_subdomain=subdomain,
        myturn_username=username,
        myturn_password=password,
        stages=stages,
        myturn_files=files,
        years=years,
    )
