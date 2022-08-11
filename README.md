# Introduction

This is the companion GitHub repository for the IN3120/IN4120 course, used to disseminate obligatory assigments and other relevant materials.

You will not be pushing anything to this repository, you will only be [pulling from it](https://github.com/git-guides/git-pull). First, you will need to [clone it](https://docs.github.com/en/github/creating-cloning-and-archiving-repositories/cloning-a-repository-from-github/cloning-a-repository).

There are five obligatory assignments in IN3120 and IN4120. In addition, there will be an obligatory [science fair](science-fair.md) for the IN4120 students.

# Code

The coding assignments assume basic familiarity with the Python language. At least [version 3.7](https://www.python.org/downloads/release) will be assumed. You can use whatever development environment you want, but you will probably be more productive and have an easier time if you use a good IDE. We can recommend [PyCharm](https://www.jetbrains.com/pycharm/). [Visual Studio Code](https://code.visualstudio.com/) is another great choice. You can use another set of tools if you want, but then don't expect help with solving challenges related to setup or tooling.

You will be provided with some "precode" or "starter code", i.e., a set of helper classes and functions that you can make use of so that you don't have to start the coding assignments completely from scratch. This precode also sets some structure on how you implement the assignments. Please familiarize yourself with what's available. The precode is commented and has some illustrative usage examples. Note the following three folders in the repository:

* [`in3120`](in3120/): The actual precode.
* [`tests`](tests/): Tests and REPL-related code. To familiarize yourself with the precode, this is a good place to start.
* [`data`](data/): Various corpora used by the tests.

The precode is in many places annotated with [type hints](https://www.python.org/dev/peps/pep-0484/). This doesn't make Python a statically typed language, but are just hints that are possible to ignore and abuse. They do convey intent and serve as a kind of additional documentation, though, and enable PyCharm and other IDEs to give you better and richer programming support.

Please strive to create readable and modular code. At a minimum, your code should pass all PyCharm's quality checks with PyCharm's standard configuration. PyCharm warns about quality issues in its right-hand scrollbar. Please fix all these before submitting your code.

# Tests

Common for the precode is that `NotImplementedError` is raised in places where you are meant to provide a working implementation. After having provided working implementations, all tests should pass. Specifically, the following should work and run without errors:

    >cd tests
    >python3 assignments.py

The above invocation runs all tests for all assignments. If you want to only run the tests for, say, assignments A and C, you can pass this as command line arguments:

    >cd tests
    >python3 assignments.py a c

An alternate way of running all tests is shown below. See [documentation](https://docs.python.org/3/library/unittest.html#command-line-interface) for the `unittest` module for more information.

    >cd tests
    >python3 -m unittest

Making tests pass for one assignment should not result in tests breaking for previous assignments. You should think of passing tests as a necessary but not sufficient condition for having your solution accepted, e.g., an implementation that makes tests pass through emitting hardcoded output targeting the tests will make the tests pass but is obviously not an acceptable solution.

If your code raises no exceptions and passes all the `assert` statements, you should see `OK` printed to the console at the end of the test run. E.g.:

    ...
    ----------------------------------------------------------------------
    Ran 33 tests in 11.898s

    OK

Tests can also be run and debugged from within PyCharm: Open up the file containing the tests in PyCharm and next to the test class or test method, in the left margin of your editor, look for a green arrow as shown [here](https://www.jetbrains.com/help/pycharm/testing-your-first-python-application.html). Clicking it will bring up a context-sensitive menu. Using the default setting of `unittest` as the default test runner should work fine.

Similarly, if you're using Visual Studio Code as your IDE, tests can be run from within the IDE. Your configuration should look something like this:

    > more .\.vscode\settings.json
    {
        "python.testing.unittestArgs": [
            "-v",
            "-s",
            "${workspaceFolder}/tests",
            "-p",
            "test_*.py"
        ],
        "python.testing.cwd": "${workspaceFolder}/tests",
        "python.testing.pytestEnabled": false,
        "python.testing.unittestEnabled": true
    }

Simple [REPLs](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) for interactive ad hoc testing from the command line can be started by specifying alternate targets, e.g.:

    >cd tests
    >python3 repl.py c

# Assignments

Individual assignments are linked to below.

Please read the assignment texts carefully before you begin. Answers to common questions are surprisingly often answered in the assignment texts. This is worth repeating: Please read the assignment texts carefully before you begin. Please also make sure that you understand the precode and the unit tests that your code is expected to pass.

* [Assignment A](assignment-a.md).
* [Assignment B](assignment-b.md).
* [Assignment C](assignment-c.md).
* [Assignment D](assignment-d.md).
* [Assignment E](assignment-e.md).

Lastly, please read the assignment texts carefully before you begin.

# Solutions

The different assignments have different deadlines. Please see the assignment texts for exact dates.

Your implementations should make all tests pass.

All your implementations should be reasonably efficient, complexity-wise. E.g., if the assignment specifies that your solution should run in logarithmic time, a solution that yields the correct output and passes all tests but that runs in quadratic time won't pass muster.

When turning in your solutions, please note the following delivery constraints that enable partial automation on the receiver side and that make life easier for the teaching assistants:

* Submit your solution using [Devilry](https://devilry.ifi.uio.no/). No emails with attachments, please.
* Your submission should be an archive in either `*.zip`, `*.tar` or `*.tar.gz` format. No other archive formats, please.
* Your implementation should only make use of [standard Python libraries](https://docs.python.org/3/library/index.html). No imports of non-standard libraries, please.
* Your implementation should be fully contained in the supplied `*.py` files. Don't introduce any new files, please.
* The files you submit for your implementation should only be the `*.py` files where there are missing implementations per the assignment. Don't submit untouched files from this repository, please, and don't spread your implementation across other files.
* Your implementation should adhere to the APIs of the abstract base classes, without modifications.

Solutions are made progressively available as the course unfolds. Simply do a `git pull` to get the solutions when published. If you get merge conflicts you are unable to resolve, as a last resort you can always nuke your copy of this repository and then re-clone it.

# Other

In addition to code for the programming assignments, this repository also contains supplementary materials for this course. In particular, note the following folders:

* [`papers`](papers/): Various papers that supplement the textbook and that are used in this course.
* [`slides`](slides/): Slides that are used as part of the lectures.
* [`exams`](exams/): Final exams from previous years, including rough solution sketches.
