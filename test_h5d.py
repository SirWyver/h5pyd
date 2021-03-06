import h5pyd
import numpy as np


if __name__ == "__main__":

    h5f = h5pyd.File("sample.h5", "a")

    # pass some sample dict
    sample_dict = {"a": [1, 5, 22.2, np.int64(20)], "b": {"c": ["monkey", "bar"], "d": np.ones((300, 300))}, 10: list(range(30))}
    h5f.create_any("first", data=sample_dict, overwrite=True)  # overwrite=True so 'first' is replaced if already exists
    h5f.create_any("second", data=np.zeros((400, 100)), overwrite=True)
    h5f.create_any("third", data=[np.zeros((400, 100)), np.ones((50, 50, 50))], overwrite=True, compression=True)
    h5f.create_any(np.int(29), data=np.zeros((30,30)), overwrite=True)
    print(h5f["first/b"])
    print(h5f["second"])  # lazy evaluated
    print(h5f["first"][10])
    print(h5f["first/b"]["d"][()])  # explizit loading
    print(h5f["third"][0][()])  # partial evaluated
