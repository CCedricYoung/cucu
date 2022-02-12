# -*- coding: utf-8 -*-
import click
import shutil
import time
import os

from click import ClickException
from cucu import fuzzy, logger
from cucu import reporter


@click.group()
@click.option('--debug/--no-debug', default=False)
def main(debug):
    """
    main entrypoint
    """
    pass


@main.command()
@click.argument('filepath')
@click.option('-b',
              '--browser',
              default='chrome',
              help='browser name to use default: chrome')
@click.option('-e',
              '--env',
              default=[],
              multiple=True,
              help='set environment variable which can be referenced with')
@click.option('-f',
              '--fail-fast/--no-fail-fast',
              default=False,
              help='stop running tests on the first failure')
@click.option('-h',
              '--headless/--no-headless',
              default=True)
@click.option('-l',
              '--logging-level',
              default='INFO',
              help='set logging level to one of debug, warn or info (default)')
@click.option('-n',
              '--name')
@click.option('-r',
              '--results',
              default='results')
@click.option('--source/--no-source',
              default=False,
              help='show the source for each step definition in the logs')
@click.option('-s',
              '--selenium-remote-url',
              default=None)
def run(filepath,
        browser,
        env,
        fail_fast,
        headless,
        logging_level,
        name,
        results,
        source,
        selenium_remote_url):
    """
    run a set of feature files
    """
    os.environ['CUCU_LOGGING_LEVEL'] = logging_level.upper()
    logger.init_logging(logging_level.upper())
    os.environ['CUCU_BROWSER'] = browser

    if headless:
        os.environ['CUCU_BROWSER_HEADLESS'] = 'True'

    if selenium_remote_url is not None:
        os.environ['CUCU_SELENIUM_REMOTE_URL'] = selenium_remote_url

    os.environ['CUCU_RESULTS_DIR'] = results
    if os.path.exists(results):
        shutil.rmtree(results)
    os.makedirs(results)

    for variable in list(env):
        key, value = variable.split('=')
        os.environ[key] = value

    args = []
    args = [
        # JUNIT xml file generated per feature file executed
        '--junit', f'--junit-directory={results}',
        # don't run disabled tests
        '--tags', '~@disabled',
        # generate a JSOn file containing the exact details of the whole run
        # '--format', 'json', f'--outfile={results}/run.json',
        '--format', 'cucu.formatter.json:CucuJSONFormatter', f'--outfile={results}/run.json',
        # use our own built in formatter
        '--format', 'cucu.formatter.cucu:CucuFormatter',
        '--logging-level', logging_level.upper(),
        # stop all log/stdout capturing
        #'--no-capture', '--no-capture-stderr', '--no-logcapture',
        # always print the skipped steps and scenarios
        '--show-skipped',
        filepath
    ]

    if source:
        args += ['--show-source']
    else:
        args += ['--no-source']

    if name is not None:
        args += ['--name', name]

    if fail_fast:
        args.append('--stop')

    from behave.__main__ import main as behave_main
    exit_code = behave_main(args)
    if exit_code != 0:
        raise ClickException('test run failed, see above for details')


@main.command()
@click.argument('filepath',
                default='results')
@click.option('-l',
              '--logging-level',
              default='INFO',
              help='set logging level to one of debug, warn or info (default)')
@click.option('-o',
              '--output',
              default='report')
def report(filepath,
           logging_level,
           output):
    """
    create an HTML test report from the results directory provided
    """
    if not os.path.exists(output):
        os.makedirs(output)

    report_location = reporter.generate(filepath, output)
    print(f'HTML test report at {report_location}')


@main.command()
def steps():
    """
    print available cucu steps
    """
    args = ['--format=steps.catalog', '--dry-run', '--no-summary']

    from behave.__main__ import main as behave_main
    exit_code = behave_main(args)
    if exit_code != 0:
        raise ClickException('listing steps failed, see above for details')


@main.command()
@click.option('-b',
              '--browser',
              default='chrome',
              help='when specified the browser will be opened with the fuzzy '
                   'js library preloaded.')
@click.option('-u',
              '--url',
              default='https://www.google.com',
              help='URL to open the browser at for debugging')
@click.option('--detach',
              default=False,
              help='when set to detach the browser will continue to run and '
                   'the cucu process will exit')
def debug(browser,
          url,
          detach):
    """
    debug cucu library
    """
    fuzzy_js = fuzzy.load_jquery_lib() + fuzzy.load_fuzzy_lib()
    # XXX: need to make this more generic once we make the underlying
    #      browser framework swappable.
    from cucu.browser.selenium import Selenium
    selenium = Selenium()
    selenium.open(browser, detach=detach)
    selenium.navigate(url)
    selenium.execute(fuzzy_js)

    if not detach:
        while True:
            # detect when there are changes to the cucu javascript library
            # and reload it in the currently running browser.
            time.sleep(5)


if __name__ == '__main__':
    main()
