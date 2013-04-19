SUBDIRS = data TumblerService TumblerTestTools

functional_tests = 				     \
		   tumblerImageFormatsUnitTests.py   \
		   tumblerSchedulersUnitTests.py     \
		   tumblerVideoFormatsUnitTests.py   \
		   tumblerFlavorsUnitTests.py        \
		   tumblerCacheUnitTests.py

configdir = $(datadir)/tumbler-tests

config_SCRIPTS = 		    \
		$(functional_tests) \
		tests.xml	    \
		run-tumbler-unit-tests.py

testrunner = run-tumbler-unit-tests.py

tests.xml: ${functional_tests}
	python2.6 generate-tests-xml.py ${testrunner} $@  ${functional_tests}

functional-test: ${functional_tests}
	@if test -h /targets/links/scratchbox.config ; then \
		export SBOX_REDIRECT_IGNORE=/usr/bin/python ; \
	fi ; \
	./${testrunner}

EXTRA_DIST = 					\
	$(config_SCRIPTS)

CLEANFILES = 					\
	tests.xml
