import nox

@nox.session
def tests(session):
    session.install("pytest")
    session.install(".")
    session.install("requests")
    session.install("tqdm")
    session.install("pandas")
    session.install("pystow")
    session.run("pytest")
