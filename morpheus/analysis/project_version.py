from morpheus.analysis.util.java_version import JavaVersion
from morpheus.analysis.util.subject import AnalysisRepo


def project_version(project: AnalysisRepo) -> JavaVersion:
    """
    If nothing defined in POM.xml, then, by default, return Java Version 13.
    """
    return JavaVersion.J13
