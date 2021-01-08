class DataModelMeta(type):
    _dataModel = {
        "system": {
            "status": {},
            "info": {},
        },
        "user": [
            {
                "id": {},
                "name": {},
                "role": {},
                "checkLogin": {},
                "operations": {
                    "create": [{}],
                    "delete": [{}],
                },
            }
        ],
        "objectConfig": {
            "network": [
                {
                    "operations": {
                        "create": {},
                        "delete": {},
                        "find": {},
                    },
                }
            ],
        },
    }

    @staticmethod
    def _get_from_model(path):
        model_data = DataModelMeta._dataModel
        model_path = ""
        for path_part in path.split("/"):
            if len(path_part) == 0:
                continue
            if isinstance(model_data, list):
                model_data = model_data[0]
                continue
            if path_part not in model_data:
                return (None, None)
            model_data = model_data[path_part]
            model_path = model_path + "/" + path_part
        return (model_path, model_data)

    @staticmethod
    def _decorate_model_object_operations(data_model, data_model_path, obj):
        if "operations" not in data_model:
            return
        for operation in data_model["operations"]:
            if obj.__full_path__().replace("/", "") == "":
                continue
            method_name = data_model_path.replace("/", "_") + "_operations_" + operation
            setattr(
                obj, operation, obj._wrapper.__getattribute__(method_name).__get__(obj)
            )
            setattr(getattr(obj, operation).__func__, "__name__", operation)

    @staticmethod
    def _decorate_model_object(obj):
        obj_name = obj._name
        (data_model_path, data_model) = DataModelMeta._get_from_model(
            obj.__data_model_path__()
        )
        if data_model is None:
            return obj
        if isinstance(data_model, list):
            setattr(
                obj,
                "_getitem_",
                lambda x: DataModelProxy(
                    wrapper=obj._wrapper,
                    name=str(x),
                    path=obj.__full_path__(),
                    model_path=obj.__data_model_path__(),
                ),
            )
            if data_model_path.endswith(obj_name):
                DataModelMeta._decorate_model_object_operations(
                    data_model[0], data_model_path, obj
                )
                return obj
            else:
                data_model = data_model[0]
        DataModelMeta._decorate_model_object_operations(
            data_model, data_model_path, obj
        )
        for key in data_model:
            if key.startswith("@") or key == "operations":
                continue
            setattr(
                obj,
                key,
                DataModelProxy(
                    wrapper=obj._wrapper,
                    name=key,
                    path=obj.__full_path__(),
                    model_path=obj.__data_model_path__(),
                ),
            )
        if obj_name not in data_model:
            for key in data_model:
                if not key.startswith("@") or ":" not in key:
                    continue
                [fieldName, fieldValue] = key.split(":")
                fieldName = fieldName.replace("@", "")
                try:
                    if obj.__cached_get__(fieldName) != fieldValue:
                        continue
                except:
                    continue
                for extField in data_model[key]:
                    ext_path = obj.__full_path__()
                    ext_dm_path = obj.__data_model_path__() + "/" + key
                    setattr(
                        obj,
                        extField,
                        DataModelProxy(
                            wrapper=obj._wrapper,
                            name=extField,
                            path=ext_path,
                            model_path=ext_dm_path,
                        ),
                    )
        return obj

    def __call__(cls, *args, **kwds):
        return DataModelMeta._decorate_model_object(type.__call__(cls, *args, **kwds))


class DataModelProxy(object, metaclass=DataModelMeta):
    def __init__(self, wrapper, name, path="", model_path=None):
        self.__cache = {}
        self._wrapper = wrapper
        self._name = name
        self._path = path
        if model_path is None:
            self._model_path = self._path
        else:
            self._model_path = model_path

    def __full_path__(self):
        return "%s/%s" % (self._path, self._name)

    def __data_model_path__(self):
        return "%s/%s" % (self._model_path, self._name)

    def __url__(self):
        return "https://%s/api%s" % (
            self._wrapper.host,
            self.__full_path__(),
        )

    def __repr__(self):
        return "proxy object for '%s' " % (self.__url__())

    def __getitem__(self, item):
        if type(item) == int:
            item = "{%s}" % item
        return self._getitem_(item)

    def get(self, *args, **kwargs):
        return self._wrapper._get(self._path + "/" + self._name, *args, **kwargs)

    def __cached_get__(self, field):
        if field not in self.__cache:
            self.__cache[field] = self._wrapper._get(
                self.__data_model_path__() + "/" + field
            )
        return self.__cache[field]

    def patch(self, value):
        return self._wrapper._patch(self._path + "/" + self._name, value)

    def set(self, value):
        return self.patch(value)

    def put(self, value):
        return self._wrapper._put(self._path + "/" + self._name, value)

    def delete(self, *args, **kwargs):
        return self._wrapper._delete(self._path + "/" + self._name, **kwargs)
