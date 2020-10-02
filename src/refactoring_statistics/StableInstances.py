from utils.log import log_init, log_close, log
import time
from os import path
from pathlib import Path
import matplotlib.pyplot as plt
from db.DBConnector import execute_query


def plot_x_y(x, y):
    fig, ax = plt.subplots()
    plt.plot(x, y)
    plt.ylabel(f"Fraction unique classes")
    plt.xlabel("commit threshold")
    plt.title(f"blabla")
    plt.ylim(ymin=1)
    fig_path = f"results/StableInstances/test.png"
    plt.savefig(fig_path)


def stable_instance_statistics():
    query = "SELECT * FROM stable_unique_classes_all_level;"
    data = execute_query(query)
    commitThresholds = data["level" == 1]["commitThreshold"]
    plot_x_y(commitThresholds, data["unique_class_files_fraction"])
    data = data.groupby("level")
    return data


log_init(f"")
log('Begin Statistics')
start_time = time.time()

Path(path.dirname("results/StableInstances/")).mkdir(parents=True, exist_ok=True)

stable_instance_statistics()

log(f"Processing statistics took {time.time() - start_time:.2f} seconds.")
log_close()

exit()
