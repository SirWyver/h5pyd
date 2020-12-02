import h5py
import numpy as np


class File:
    _atomics = (
        int,
        float,
        bool,
        str,
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
        np.float16,
        np.float32,
        np.float64,
        np.bool_,
        np.complex64,
        np.complex128,
        np.generic,
        np.ndarray,
    )
    _collections = (dict, list, tuple)

    def __init__(
        self,
        name,
        mode=None,
        driver=None,
        libver=None,
        userblock_size=None,
        swmr=False,
        rdcc_nslots=None,
        rdcc_nbytes=None,
        rdcc_w0=None,
        track_order=None,
        fs_strategy=None,
        fs_persist=False,
        fs_threshold=1,
        **kwds,
    ):
        self.file = h5py.File(
            name,
            mode,
            driver,
            libver,
            userblock_size,
            swmr,
            rdcc_nslots,
            rdcc_nbytes,
            rdcc_w0,
            track_order,
            fs_strategy,
            fs_persist,
            fs_threshold,
            **kwds,
        )

    def __repr__(self):
        return self.file.__repr__()

    def create_any(self, name, data, compression=None, overwrite=False, **kwds):
        if isinstance(name, tuple):
            dname = "/".join(map(str, name))
        else:
            dname = str(name)
        if overwrite and dname in self.file:
            del self.file[dname]
        if isinstance(data, self._atomics):

            h5_data = self.file.create_dataset(name=dname, data=data, compression=compression, **kwds)
            h5_data.attrs["_type"] = type(data).__name__
            h5_data.attrs["_name_type"] = "str" if isinstance(name, str) else type(name[-1]).__name__
        elif isinstance(data, self._collections):
            h5_group = self.file.create_group(name=dname, track_order=True, **kwds)
            h5_group.attrs["_type"] = type(data).__name__
            h5_group.attrs["_name_type"] = "str" if isinstance(name, str) else type(name[-1]).__name__

            if isinstance(data, dict):
                for k, v in data.items():
                    next_name = (name, k) if isinstance(name, str) else (*name, k)
                    self.create_any(name=next_name, data=v, compression=compression, overwrite=overwrite, **kwds)
            else:
                # auto-generate keys for list/tuple
                for k, v in enumerate(data):
                    next_name = (name, k) if isinstance(name, str) else (*name, k)
                    self.create_any(name=next_name, data=v, compression=compression, overwrite=overwrite, **kwds)
        else:
            raise IOError(f"Data type {data.type} not supported")

    def _get_any(self, name, lazy=True):
        ret = None
        if isinstance(name, tuple):
            dname = "/".join(map(str, name))
        else:
            dname = str(name)

        res = self.file[dname]
        if "_type" not in res.attrs:
            ret = res
            org_name_type = None
        else:
            org_type = res.attrs["_type"]
            org_name_type = res.attrs["_name_type"]
            if org_type in [x.__name__ for x in self._atomics]:
                ret = res
                if org_type != "ndarray" or not lazy:
                    # non-lazy
                    ret = ret[()]
                if org_type == "str":
                    ret = ret.decode()
            elif org_type in [x.__name__ for x in self._collections]:
                if org_type == "dict":
                    ret = dict()
                else:
                    ret = []
                for k in res.keys():
                    if org_type == "dict":
                        next_name = (name, k) if isinstance(name, str) else (*name, k)
                        ret_k, k_name_type = self._get_any(name=next_name, lazy=lazy)
                        k_name = k if k_name_type == "str" else next(x for x in self._atomics if x.__name__ == k_name_type)(k)
                        ret[k_name] = ret_k
                    else:
                        next_name = (name, k) if isinstance(name, str) else (*name, k)
                        ret.append(self._get_any(name=next_name, lazy=lazy)[0])
                if org_type == "tuple":
                    ret = tuple(ret)
            else:
                raise IOError(f"Cannot convert org_type {org_type}")
        return ret, org_name_type

    def __getitem__(self, name):
        return self._get_any(name)[0]

    def __setitem__(self, name, data):
        self.create_any(name, data)

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    # from File
    def close(self):
        self.file.close()

    def flush(self):
        self.file.flush()

    @property
    def id(self):
        return self.file.id

    @property
    def filename(self):
        return self.file.filename

    @property
    def mode(self):
        return self.file.mode

    @property
    def swmr_mode(self):
        return self.file.swmr_mode

    @property
    def driver(self):
        return self.file.driver

    @property
    def libver(self):
        return self.file.libver

    @property
    def userblock_size(self):
        return self.file.userblock_size

    # from Group
    def __iter__(self):
        return self.file.__iter__()

    def __contains__(self):
        return self.file.__contains__()

    def __bool__(self):
        return self.file.__bool__()

    def keys(self):
        return self.file.keys()

    def values(self):
        return self.file.values()

    def items(self):
        return self.file.items()

    def get(self, name, default=None, getclass=False, getlink=False):
        return self.file.get(name, default, getclass, getlink)

    def visit(self, callable):
        return self.file.visit(callable)

    def visititems(self, callable):
        return self.file.visititems(callable)

    def copy(
        self,
        source,
        dest,
        name=None,
        shallow=False,
        expand_soft=False,
        expand_external=False,
        expand_refs=False,
        without_attrs=False,
    ):
        return self.file.copy(source, dest, name, shallow, expand_soft, expand_external, expand_refs, without_attrs)

    def create_dataset(self, name, shape=None, dtype=None, data=None, **kwds):
        return self.file.create_dataset(name, shape=shape, dtype=dtype, data=data, **kwds)

    def require_dataset(self, name, shape=None, dtype=None, exact=None, **kwds):
        return self.file.require_dataset(name, shape=shape, dtype=dtype, exact=exact, **kwds)

    def create_dataset_like(self, name, other, **kwds):
        return self.file.create_dataset_like(name, other, **kwds)

    def create_virtual_dataset(name, layout, fillvalue=None):
        return self.file.create_virtual_dataset(name, layout, fillvalue=fillvalue)

    @property
    def attrs(self):
        return self.file.attrs

    @property
    def ref(self):
        return self.file.ref

    @property
    def regionref(self):
        return self.file.regionref

    @property
    def name(self):
        return self.file.name

    @property
    def parent(self):
        return self.file.parent
