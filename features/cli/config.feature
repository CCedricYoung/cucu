Feature: Config
  As a developer I want the user to get the expected variable and config
  behavior when using cucu

  Scenario: User can load cucurc values from a cucucrc file in
    Given I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc/cucurc.yml" with the following:
      """
      FOO: bar
      FIZZ: booze
      BUZZ: wah
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc/directory/cucurc.yml" with the following:
      """
      FIZZ: buzz
      BUZZ: wat
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_nested_cucurc/directory/feature_that_prints.feature" with the following:
      """
      Feature: Feature file that prints some variables

        Scenario: This scenario prints a bunch of variables
         Given I echo "\{FOO\}"
           And I echo "\{FIZZ\}"
           And I echo "\{BUZZ\}"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/load_nested_cucurc --results={CUCU_RESULTS_DIR}/nested_cucurc_results --env BUZZ=buzz" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "0"
     Then I should see "{STDOUT}" matches the following:
       """
       Feature: Feature file that prints some variables

         Scenario: This scenario prints a bunch of variables
       bar

           Given I echo "\{FOO\}"      #  in .*
           # FOO="bar"
       booze

             And I echo "\{FIZZ\}"     #  in .*
             # FIZZ="booze"
       buzz

             And I echo "\{BUZZ\}"     #  in .*
             # BUZZ="buzz"

       1 feature passed, 0 failed, 0 skipped
       1 scenario passed, 0 failed, 0 skipped
       3 steps passed, 0 failed, 0 skipped, 0 undefined
       [\s\S]*
       """

  Scenario: User gets an appropriate error when cuucrc has invalid syntax
    Given I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/environment.py" with the following:
      """
      from cucu.environment import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/steps/__init__.py" with the following:
      """
      from cucu.steps import *
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/cucurc.yml" with the following:
      """
      FOO: bar
      completely=broken
      """
      And I create a file at "{CUCU_RESULTS_DIR}/load_bad_cucurc/directory/feature_that_prints.feature" with the following:
      """
      Feature: Feature tries to print something

        Scenario: This scenario prints the value of FOO
         Given I echo "\{FOO\}"
      """
     When I run the command "cucu run {CUCU_RESULTS_DIR}/load_bad_cucurc --results={CUCU_RESULTS_DIR}/nested_cucurc_results" and save stdout to "STDOUT", stderr to "STDERR" and expect exit code "1"
     Then I should see "{STDOUT}" is empty
      And I should see "{STDERR}" contains "yaml.scanner.ScannerError: while scanning a simple key"
