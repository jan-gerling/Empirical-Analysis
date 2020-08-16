from configs import Level, LEVEL_MAP
from refactoring_statistics.plot_utils import plot_errorbar
from refactoring_statistics.query_utils import query_aggregate
from utils.log import log_init, log_close, log
import time
from os import path
from pathlib import Path


log_init(f"")
log('Begin Statistics')
start_time = time.time()

Path(path.dirname("results/Aggregate/")).mkdir(parents=True, exist_ok=True)

for level in Level:
    refactorings = LEVEL_MAP[level]
    if len(refactorings) > 0:
        for table_name in ["refactoringspercommit"]:
            avg, label = query_aggregate(table_name, "AVG", refactorings, str(level))
            std, label = query_aggregate(table_name, "STD", refactorings, str(level))
            var, label = query_aggregate(table_name, "VARIANCE", refactorings, str(level))
            plot_errorbar(refactorings, avg["AVG"], var["VARIANCE"], "VARIANCE", f"{table_name}_{str(level)}")


log(f"Processing statistics took {time.time() - start_time:.2f} seconds.")
log_close()

exit()
