import nox

@nox.session
def tests(session):
    args = session.posargs or []
    session.install(".")
    session.install("pytest")
    session.install("tqdm")
    session.install("pandas")
    session.install("pystow")
    session.run("pytest", *args)

