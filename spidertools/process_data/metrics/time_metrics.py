import math
import numpy as np
import dateutil

from subprocess import Popen, PIPE
from datetime import datetime, date
from typing import List

def calc_mean_prod_test_diff(test_change: List[date], prod_change: List[date]):
    if len(test_change) == 0 and len(prod_change) == 0:
        return 0
    elif len(test_change) == 0:
        return -1
    elif len(prod_change) == 0:
        return -1
    
    def mean(date_list : List[date]):
        mean = (np.array(date_list, dtype='datetime64[s]')
            .view('i8')
            .mean()
            .astype('datetime64[s]'))

        return mean.astype(date)

    return (mean(prod_change) - mean(test_change)).days


def calc_median_prod_test_diff(test_change: List[date], prod_change: List[date]):
    if len(test_change) == 0 and len(prod_change) == 0:
        return 0
    elif len(test_change) == 0:
        return -1
    elif len(prod_change) == 0:
        return -1
    
    prod_median = prod_change[math.floor(len(prod_change)/2)]
    test_median = test_change[math.floor(len(test_change)/2)]

    difference = prod_median - test_median
    return difference.days


def calculate_age(method, today: date) -> int:
    first_commit = method['commits'][-1]
    first_commit_date = date.fromisoformat(first_commit['date'])
    difference = today - first_commit_date

    return difference.days

def average_commit_interval(commits):
    if len(commits) <= 1:
        return 0

    total_commits = len(commits)

    return calc_change_age_window(commits) / total_commits

def calc_change_age_window(commits):
    if len(commits) <= 1:
        return 0
    
    first_commit :date = date.fromisoformat(commits[-1]['date'])
    last_commit :date = date.fromisoformat(commits[0]['date'])

    difference = last_commit - first_commit 

    return difference.days

def get_commit_date(sut_path, present_commit) -> date:
    show_p = Popen(f"git show -s --format=%ci {present_commit}", cwd=sut_path, stdout=PIPE, shell=True)
    date_present_bytes = show_p.communicate()[0]
    date_present_string = date_present_bytes.decode('utf8')
    result = dateutil.parser.parse(date_present_string)
    return result.date()