import click
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader
import json
import os
from smaker.runner import SnakeRunner
import sys

def list_endpoints(runners):
    return [ print(e) for r in runners for e in r.endpoints ]

def run_endpoint(endpoint, runners, api_opts):
    matching = [sn for sn in runners if sn.endpoints.get(endpoint, None) != None]
    assert len(matching) != 0, 'Endpoint not found: %s' % endpoint
    assert len(matching) == 1, 'Endpoint found in multiple runners: %s' % endpoint
    for opt in ['snakefile', 'configfile']: api_opts.pop(opt, None)
    matching[0].run(endpoint, api_opts)

def run_on_the_fly(snakefile, configfile, extra_modules, extra_sources, workflow_opts, api_opts):
    workflow_opts['modules'] = { os.path.dirname(os.path.normpath(mod)): mod for mod in extra_modules if os.path.isfile(mod) }
    workflow_opts['sources'] = list(extra_sources)
    SnakeRunner.run_undefined_endpoint(configfile, snakefile, workflow_opts, api_opts)

@click.command(name='smaker', context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.argument('cmd')
@click.option('--endpoint', '-e', required=False)
@click.option('--construct', default='Smakefile')
@click.option('--module', multiple=True)
@click.option('--source', multiple=True)
@click.option('--snakefile', '-s', type=str, required=False)
@click.option('--configfile', '-c', type=str, required=False)
@click.option('--dryrun/--no-dryrun', '-n/-p', is_flag=True, default=True)
@click.option('--quiet/--verbose', '-q/-v', is_flag=True, default=False)
@click.option('--cores', type=int, default=2)
@click.option('--rulegraph', is_flag=True, default=False)
@click.option('--reason', is_flag=True, default=False)
@click.option('--summary', is_flag=True, default=False)
@click.option('--print-shell', is_flag=True, default=False)
@click.option('--forceall', '-F', is_flag=True, default=False)
@click.option('--unlock/--no-unlock', is_flag=True, default=False)
@click.pass_context
def main(context, cmd, endpoint, construct, module, source, snakefile, configfile, dryrun, quiet,
         cores, rulegraph, reason, summary, print_shell, forceall, unlock):
    """Smaker workflow tool

    The `run` command is used to execute pre-defined endpoints in a
    construct file (default=Smakefile).

    `run` usage:

        smaker run [api_opts] endpoint
        smaker run endpoint [api_opts]

    Use the `list` command to view pre-defined endpoints:

    `list` usage:

        smaker list

    Use the `fly` command to dynamically create and run  endpoints
    in the same manner you would statically with a construct file.
    "Fly" can also be used to run regular `Snakefile`s.
    `--snakefile` and `--configfile` are required parameters for
    this endpoint.

    `fly` usage:
        smaker fly [api_opts] - [workflow_opts]

        smaker fly --snakefile SNAKEFILE --configfile CONFIG [api_opts] - [workflow_opts]

    `api_opts` and `workflow_opts` are distinguished in the context of
    the Snakemake API. Options like `--dryrun, `--quiet`, and `--cores`
    are passed to the snakemake library runtime, while workflow options
    are passed to user-defined workflow rules. The `--snakefile` and `--configfile`
    apt_opts are ignored with the `run` command to maintain consistency between run-time
    and version-controlled configurations. Workflow opts valued "True/true" or "False/false"
    are converted boolean.
    """

    if cmd == 'run': assert endpoint != None, 'Run requires endpoint name.\nUsage: "smaker run -e [endpoint]"'

    # "import construct as construct_module"
    assert os.path.isfile(construct), 'Construct file not found: %s' % construct
    spec = spec_from_loader("Smakefile", SourceFileLoader("Smakefile", construct))
    cmodule = module_from_spec(spec)
    spec.loader.exec_module(cmodule)

    try:
        workflow_opts = [ opt for arg in context.args for opt in arg.split('=') ]
        workflow_opts = { '_'.join(workflow_opts[i][2:].split('-')): workflow_opts[i+1] for i in range(0, len(workflow_opts), 2) }
        true_opts = { k: True for k,v in workflow_opts.items() if v in ['True', 'true'] }
        false_opts = { k: False for k,v in workflow_opts.items() if v in ['False', 'false'] }
        workflow_opts.update(true_opts)
        workflow_opts.update(false_opts)
    except:
        print('Misformatted arguments:\n%s' % context.args)
        raise

    runners = [ getattr(cmodule, val) for val in dir(cmodule) if isinstance(getattr(cmodule, val), SnakeRunner) ]
    api_opts = { 'cores': cores, 'quiet': quiet, 'dryrun': dryrun , 'unlock': unlock, 'printrulegraph': rulegraph, 'printreason': reason, 'summary':
                summary, 'printshellcmds': print_shell, 'forceall': forceall }

    if cmd == 'list': list_endpoints(runners)
    elif cmd == 'run': run_endpoint(endpoint, runners, api_opts)
    elif cmd == 'fly': run_on_the_fly(snakefile, configfile, module, source, workflow_opts, api_opts)
    else:
        print('Command not recognized: %s' % cmd)
        raise

if __name__=='__main__':
    main()

