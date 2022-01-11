import nox


@nox.session
def tests_without_tqdm(session):
    session.install("pytest")
    session.install("requests")
    session.run("pytest")


@nox.session
def tests(session):
    session.install("pytest")
    session.install("requests")
    session.install("tqdm")
    session.run("pytest")
