import matplotlib.pyplot as plt
import numpy as np
from configs import Level, LEVEL_MAP
from db.DBConnector import execute_query
from utils.log import log_init, log_close, log
import time
from os import path
from pathlib import Path


def query_db_commit(table_name: str, refactorings):
    data = []
    for refactoring_name in refactorings:
        query = f"SELECT `{refactoring_name}` FROM {table_name} WHERE `{refactoring_name}` > 0"
        refactoringspercommit = execute_query(query).values
        data.append(refactoringspercommit)

    log(f"Got the raw data from {table_name} for commits.")
    return data


log_init(f"")
log('Begin Statistics')
start_time = time.time()

Path(path.dirname("results/Distribution/")).mkdir(parents=True, exist_ok=True)

for level in Level:
    refactorings = LEVEL_MAP[level]
    if len(refactorings) > 0:
        #commit
        data = query_db_commit("refactoringspercommit", refactorings)

        fig, ax = plt.subplots(figsize=(len(refactorings), 8), dpi=240)
        ax.set_title(f"Refactoring type distribution per commit for (level={str(level)})")
        ax.violinplot(data, points=1000, showmeans=False, showextrema=False, showmedians=True)
        plt.xticks(np.arange(len(refactorings)), refactorings, rotation=20)
        plt.yscale("log")
        fig_path = f"results/Distribution/commit_refactoringspercommit_{str(level)}.png"
        plt.savefig(fig_path)


log(f"Processing statistics took {time.time() - start_time:.2f} seconds.")
log_close()

exit()
