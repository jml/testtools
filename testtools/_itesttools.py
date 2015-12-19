# Copyright (c) 2015 testtools developers. See LICENSE for details.
"""Interfaces used within testtools."""

from zope.interface import Attribute, Interface


class IRunnable(Interface):
    """A thing that a test runner can run."""

    def __call__(result=None):
        """Equivalent to ``run``."""

    def countTestCases():
        """Return the number of tests this represents."""

    def debug():
        pass

    def run(result=None):
        """Run the test."""


class ITestSuite(IRunnable):
    """A suite of tests."""

    def __iter__():
        """Iterate over the IRunnables in suite."""


class ITestCase(IRunnable):
    """An individual test case."""

    def __str__():
        """Return a short, human-readable description."""

    def id():
        """A unique identifier."""

    def shortDescription(self):
        """Return a short, human-readable description."""


class IExceptionHandler(Interface):
    """Handle an exception from user code."""

    def __call__(test_case, test_result, exception_value):
        """Handle an exception raised from user code.

        :param TestCase test_case: The test that raised the exception.
        :param TestResult test_result: Where to report the result to.
        :param Exception exception_value: The raised exception.
        """


class IRunTestFactory(Interface):
    """Create a ``RunTest`` object."""

    def __call__(test_case, exception_handlers, last_resort=None):
        """Construct and return a ``RunTest``.

        :param ITestCase+ITestCaseStrategy test_case: The test case to run.
        :param exception_handlers: List of (exception_type, IExceptionHandler).
            This list can be mutated any time.
        :param IExceptionHandler last_resort: exception handler to be used as
            a last resort.

        :return: An ``IRunTest``.
        """


class IRunTest(Interface):
    """Called from inside ITestCase.run to actually run the test."""

    # XXX: jml thinks this ought to be run(case, result), and IRunTestFactory
    # shouldn't take a test_case at all.
    def run(result):
        """Run the test."""


# TODO:
# - legacy test result interfaces
# - document which test result interfaces are expected above
# - make TestControl an interface, use it by composition in
#   ExtendedToOriginalDecorator
# - figure out whether .errors, .skip_reasons, .failures, etc. should be
#   on IExtendedTestResult or on a separate interface that TestResult also
#   implements
# - figure out what to do about failfast and tb_locals
# - interface for TagContext?
# - failureException?
# - loading stuff, e.g. test_suite, load_tests?
# - Matchers, Mismatch?
# - Tests for interface compliance
# - Tests to make sure that users of objects are relying only on their
#   interfaces and not the implementation
# - Identify code that's intended to be used by subclassing and try to
#   deprecate / limit that usage (or at least make an easily greppable note).


class ITestCaseStrategy(ITestCase):
    """What ``RunTest`` needs to run a test case.

    This is a test that has a ``setUp``, a test body, and a ``tearDown``.

    Must also be an ``ITestCase`` so the results can be reported.
    """

    """Should local variables be captured in tracebacks?

    Can be mutated externally.
    """
    __testtools_tb_locals__ = Attribute('__testtools_tb_locals__')

    """List of ``(function, args, kwargs)`` called in reverse order after test.

    This list is mutated by ``RunTest``.
    """
    _cleanups = Attribute('_cleanups')

    """If non-False, then force the test to fail regardless of behavior.

    If not defined, assumed to be False.
    """
    force_failure = Attribute('force_failure')

    def defaultTestResult():
        """Construct a test result object for reporting results."""

    def _get_test_method():
        """Get the test method we are exercising."""

    def _run_setup(result):
        """Run the ``setUp`` method of the test."""

    def _run_test_method(result):
        """Run the test method.

        Must run the method returned by _get_test_method.
        """

    def _run_teardown(result):
        """Run the ``tearDown`` method of the test."""

    def getDetails():
        """Return a mutable dict mapping names to ``Content``."""

    def onException(exc_info, tb_label):
        """Called when we receive an exception.

        :param exc_info: A tuple of (exception_type, exception_value,
            traceback).
        :param tb_label: Used as the label for the traceback, if the traceback
            is to be attached as a detail.
        """


class IExtendedTestResult(Interface):
    """Receives test events."""

    def addExpectedFailure(test, err=None, details=None):
        """``test`` failed with an expected failure.

        For any given test, must be called after ``startTest`` was called for
        that test, and before ``stopTest`` has been called for that test.

        :param ITestCase test: The test that failed expectedly.
        :param exc_info err: An exc_info tuple.
        :param dict details: A map of names to ``Content`` objects.
        """

    def addError(test, err=None, details=None):
        """``test`` failed with an unexpected error.

        For any given test, must be called after ``startTest`` was called for
        that test, and before ``stopTest`` has been called for that test.

        :param ITestCase test: The test that raised an error.
        :param exc_info err: An exc_info tuple.
        :param dict details: A map of names to ``Content`` objects.
        """

    def addFailure(test, err=None, details=None):
        """``test`` failed as assertion.

        For any given test, must be called after ``startTest`` was called for
        that test, and before ``stopTest`` has been called for that test.

        :param ITestCase test: The test that raised an error.
        :param exc_info err: An exc_info tuple.
        :param dict details: A map of names to ``Content`` objects.
        """

    def addSkip(test, reason=None, details=None):
        """``test`` was skipped, rather than run.

        For any given test, must be called after ``startTest`` was called for
        that test, and before ``stopTest`` has been called for that test.

        :param ITestCase test: The test that raised an error.
        :param reason: The reason for the test being skipped.
        :param dict details: A map of names to ``Content`` objects.
        """

    def addSuccess(test, details=None):
        """``test`` run successfully.

        For any given test, must be called after ``startTest`` was called for
        that test, and before ``stopTest`` has been called for that test.

        :param ITestCase test: The test that raised an error.
        :param dict details: A map of names to ``Content`` objects.
        """

    def addUnexpectedSuccess(test, details=None):
        """``test`` was expected to fail, but succeeded.

        For any given test, must be called after ``startTest`` was called for
        that test, and before ``stopTest`` has been called for that test.

        :param ITestCase test: The test that raised an error.
        :param dict details: A map of names to ``Content`` objects.

        """

    def wasSuccessful():
        """Has this result been successful so far?"""

    def startTestRun():
        """Started a run of (potentially many) tests."""

    def stopTestRun():
        """Finished a run of (potentially many) tests."""

    def startTest(test):
        """``test`` started executing.

        Must be called after ``startTestRun`` and before ``stopTestRun``.

        :param ITestCase test: The test that started.
        """

    def stopTest(test):
        """``test`` stopped executing.

        Must be called after ``startTestRun`` and before ``stopTestRun``.

        :param ITestCase test: The test that stopped.
        """

    def tags(new_tags, gone_tags):
        """Change tags for the following tests.

        Updates ``current_tags`` such that all tags in ``new_tags`` are in
        ``current_tags`` and none of ``gone_tags`` are in ``current_tags``.

        :param set new_tags: A set of tags that will be applied to any
            following tests.
        :param set gone_tags: A set of tags that will no longer be applied to
            following tests.
        """

    def time(timestamp):
        """Tell the test result what the current time is.

        :param datetime timestamp: Either a time with timezone information, or
            ``None`` in which case the test result should get time from the
            system.
        """


class IStreamResult(Interface):
    """A test result for reporting the activity of a test run.

    Typical use

      >>> result = StreamResult()
      >>> result.startTestRun()
      >>> try:
      ...     case.run(result)
      ... finally:
      ...     result.stopTestRun()

    The case object will be either a TestCase or a TestSuite, and
    generally make a sequence of calls like::

      >>> result.status(self.id(), 'inprogress')
      >>> result.status(self.id(), 'success')

    General concepts

    StreamResult is built to process events that are emitted by tests during a
    test run or test enumeration. The test run may be running concurrently, and
    even be spread out across multiple machines.

    All events are timestamped to prevent network buffering or scheduling
    latency causing false timing reports. Timestamps are datetime objects in
    the UTC timezone.

    A route_code is a unicode string that identifies where a particular test
    run. This is optional in the API but very useful when multiplexing multiple
    streams together as it allows identification of interactions between tests
    that were run on the same hardware or in the same test process. Generally
    actual tests never need to bother with this - it is added and processed
    by StreamResult's that do multiplexing / run analysis. route_codes are
    also used to route stdin back to pdb instances.

    The StreamResult base class does no accounting or processing, rather it
    just provides an empty implementation of every method, suitable for use
    as a base class regardless of intent.
    """

    def startTestRun():
        """Start a test run.

        This will prepare the test result to process results (which might imply
        connecting to a database or remote machine).
        """

    def stopTestRun():
        """Stop a test run.

        This informs the result that no more test updates will be received. At
        this point any test ids that have started and not completed can be
        considered failed-or-hung.
        """

    def status(test_id=None, test_status=None, test_tags=None, runnable=True,
               file_name=None, file_bytes=None, eof=False, mime_type=None,
               route_code=None, timestamp=None):
        """Inform the result about a test status.

        :param test_id: The test whose status is being reported. None to
            report status about the test run as a whole.
        :param test_status: The status for the test. There are two sorts of
            status - interim and final status events. As many interim events
            can be generated as desired, but only one final event. After a
            final status event any further file or status events from the
            same test_id+route_code may be discarded or associated with a new
            test by the StreamResult. (But no exception will be thrown).

            Interim states:
              * None - no particular status is being reported, or status being
                reported is not associated with a test (e.g. when reporting on
                stdout / stderr chatter).
              * inprogress - the test is currently running. Emitted by tests
                when they start running and at any intermediary point they
                might choose to indicate their continual operation.

            Final states:
              * exists - the test exists. This is used when a test is not being
                executed. Typically this is when querying what tests could be
                run in a test run (which is useful for selecting tests to run).
              * xfail - the test failed but that was expected. This is purely
                informative - the test is not considered to be a failure.
              * uxsuccess - the test passed but was expected to fail. The test
                will be considered a failure.
              * success - the test has finished without error.
              * fail - the test failed (or errored). The test will be
                considered a failure.
              * skip - the test was selected to run but chose to be skipped.
                e.g. a test dependency was missing. This is purely informative-
                the test is not considered to be a failure.

        :param test_tags: Optional set of tags to apply to the test. Tags
            have no intrinsic meaning - that is up to the test author.
        :param runnable: Allows status reports to mark that they are for
            tests which are not able to be explicitly run. For instance,
            subtests will report themselves as non-runnable.
        :param file_name: The name for the file_bytes. Any unicode string may
            be used. While there is no semantic value attached to the name
            of any attachment, the names 'stdout' and 'stderr' and 'traceback'
            are recommended for use only for output sent to stdout, stderr and
            tracebacks of exceptions. When file_name is supplied, file_bytes
            must be a bytes instance.
        :param file_bytes: A bytes object containing content for the named
            file. This can just be a single chunk of the file - emitting
            another file event with more later. Must be None unleses a
            file_name is supplied.
        :param eof: True if this chunk is the last chunk of the file, any
            additional chunks with the same name should be treated as an error
            and discarded. Ignored unless file_name has been supplied.
        :param mime_type: An optional MIME type for the file. stdout and
            stderr will generally be "text/plain; charset=utf8". If None,
            defaults to application/octet-stream. Ignored unless file_name
            has been supplied.
        """
