from cucu.language_server.core import find_completions, load_cucu_steps


def test_find_completions_returns_prefix_matches_first():
    matches = find_completions('I click the ')

    # the completions should only contain matches that are prefixed by the
    # `I click the ` text
    for (step_name, _) in matches:
        assert step_name.startswith('I click the ')


def test_find_completions_returns_something_when_prefix_does_not_match():
    matches = find_completions('click button')

    # the completions are based on levenshtein distance so lets just assert
    # that at least one of the words we included in our search are in the
    # resulting matching step names
    for (step_name, _) in matches:
        assert step_name.find('click') != -1 or step_name.find('button') != -1


def test_load_cucu_steps_returns_valid_list_of_existing_steps():
    steps = load_cucu_steps()

    for step_name in steps.keys():
        step_details = steps[step_name]

        assert type(step_name) == str
        assert 'location' in step_details
        assert 'filepath' in step_details['location']
        assert 'line' in step_details['location']
