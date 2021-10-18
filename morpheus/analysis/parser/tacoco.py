import re
from sqlalchemy import and_
from sqlalchemy import exc
from typing import Dict, List, Tuple
from morpheus.analysis.parser.parsing_engines import parse_tacoco_test_string
from morpheus.database.models.methods import ProdMethodVersion, TestMethod, LineCoverage
from morpheus.database.models.repository import Commit, Project
import logging
import timeit
from morpheus.analysis.util.memoize import memoize

logger = logging.getLogger(__name__)

class TacocoParser():
    def parse(self, tacoco_dict: Dict) -> List[Tuple[TestMethod, LineCoverage]]:
        logger.info("Start parsing tacoco data...")

        # Testcases
        test_map: Dict[int, Tuple[TestMethod, str]] = {}
        if 'testsIndex' in tacoco_dict:
            for idx, test_string in enumerate(tacoco_dict['testsIndex']):
                try:
                    test, result = self.__parse_test_method(test_string)
                except:
                    logger.error("Failed parsing: %s %s", idx, test_string)
                    continue        
                test_map[idx] = (test, result)
        
        # Coverage
        coverage: Dict[int, List[LineCoverage]] = dict()
        if 'sources' in tacoco_dict:
            for source in tacoco_dict['sources']:
                start_line: int = source["source"]["firstLine"]
                
                # create a map from test to covered lines.
                testStmtMatrix = source['testStmtMatrix']
                for test_id, matrix in zip(source['activatingTests'], testStmtMatrix):

                    # Check if test_id is in the map, if not skip it
                    if test_id not in test_map:
                        continue
                    
                    # Create a representation for each line covered by the test
                    for i, covered in enumerate(matrix):
                        line_num = i + start_line

                        #  Skip lines that are not not covered
                        if not covered:
                            continue

                        line = LineCoverage(
                            full_name=source["source"]["fullName"],
                            line_number=line_num,
                        )
                        
                        # If test case already in coverage add the line so we know it covers muliple lines.
                        if test_id in coverage:
                            lines = coverage[test_id]
                            lines.append(line)
                            coverage[test_id] = lines
                        else:
                            coverage[test_id] = [line]

        # Merge to dictionaries and return a list of tuples
        def _merge(idx) -> Tuple[TestMethod, str, List[LineCoverage]]:
            test : TestMethod
            result: str
            
            if idx in test_map and idx in coverage:
                test, result = test_map[idx]
                line_coverage: List[LineCoverage] = coverage[idx]

                for line in line_coverage: 
                    line.test_result = result

                return test, line_coverage
            
        result = list(map(_merge, coverage.keys()))
        logger.info("Finished parsing tacoco data...")
        return result

    def __parse_test_method(self, test_method: str) -> Tuple[TestMethod, str]:
        try:
            (package_name, class_name, method_name, is_passing) = parse_tacoco_test_string(test_method)
        except:
            logger.error("method_name error: %s", test_method)
            raise Exception("[ERROR] method_name error: {}".format(test_method))

        test = TestMethod(package_name=package_name ,class_name=class_name, method_name=method_name)
        return test, is_passing

    def store(self,
            session,
            project: Project,
            commit: Commit,
            coverage: List[Tuple[TestMethod, List[LineCoverage]]]
        ):

        start_time = timeit.default_timer()
        for test, _ in coverage:
            test.project_id = project.id

            if (test_id := session.query(TestMethod.id)\
                .filter(
                    TestMethod.project_id==test.project_id,
                    TestMethod.package_name==test.package_name,
                    TestMethod.class_name==test.class_name,
                    TestMethod.method_name==test.method_name,
                ).scalar()) is None:
                session.add(test)
            else:
                test.id = test_id

        logger.debug('Iterating through tests: %s', timeit.default_timer() - start_time)

        start_time = timeit.default_timer()
        session.commit()
        logger.debug('Adding tests to database: %s', timeit.default_timer() - start_time)

        start_time = timeit.default_timer()

        @memoize
        def __get_method_version_id(commid_id: int, full_name: str, line_number: int):
            return session.query(ProdMethodVersion.id) \
                    .filter(
                        and_(
                            ProdMethodVersion.commit_id == commid_id,
                            ProdMethodVersion.file_path.contains(full_name),
                            ProdMethodVersion.line_start <= line_number,
                            ProdMethodVersion.line_end >= line.line_number,
                        )
                    ).first()

        for test, lines in coverage:
            if test.id is None:
                logger.error("Test not stored in database %s.%s.%s project_id: %s", test.package_name, test.class_name, test.method_name, test.project_id)
                continue

            for line in lines:
                result = __get_method_version_id(commit.id, line.full_name, line.line_number)
                
                line.commit_id = commit.id
                line.test_id = test.id

                if result is None:
                    # logger.warn("Line version not stored: %s, %s, %s, %s, %s, %s, %s", line.id, line.commit_id, line.test_id, line.method_version_id, line.test_result, line.full_name, line.line_number)
                    continue

                (line.method_version_id, ) = result

                # if line.commit_id == 2 and line.test_id == 2599 and line.method_version_id==1760  and line.line_number == 173:
                #     logger.debug("Test: %s, %s, %s, %s", test.id, test.method_name, test.class_name, test.package_name)
                
                session.add(line)

        logger.debug('Iterating through lines: %s', timeit.default_timer() - start_time)

        start_time = timeit.default_timer()
        session.commit()
        logger.debug('Adding lines to database: %s', timeit.default_timer() - start_time)