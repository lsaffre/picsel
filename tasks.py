from atelier.invlib.dummy import ns
ns.setup_from_tasks(
    globals(), # "picsel",
    blogref_url="http://luc.lino-framework.org",
    revision_control_system='git',
    # tolerate_sphinx_warnings=True,
    cleanable_files=['docs/api/picsel.*'])

