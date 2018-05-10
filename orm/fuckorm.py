from orm import mysql_singleton


class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name  # 列名
        self.column_type = column_type  # 数据类型
        self.primary_key = primary_key  # 是否为主键
        self.default = default  # 默认值


class StringField(Field):
    def __init__(self, name=None, ddl='varchar(100)', primary_key=False, default=None):
        super().__init__(name, ddl, primary_key, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'int', primary_key, default)


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        table_name = attrs.get('table_name', None)
        if not table_name:
            raise TypeError('没有表名')
        primary_key = None  # 查找primary_key字段

        # 保存列类型的对象
        mappings = dict()
        for k, v in attrs.items():
            # 是列名的就保存下来
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primary_key:
                        raise TypeError('主键重复: %s' % k)
                    primary_key = k

        for k in mappings.keys():
            attrs.pop(k)
        if not primary_key:
            raise TypeError('没有主键')

        # 给cls增加一些字段：
        attrs['mapping'] = mappings
        attrs['primary_key'] = primary_key
        attrs['table_name'] = table_name
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):  # .访问属性触发
        try:
            return self[key]
        except KeyError:
            raise AttributeError('没有属性：%s' % key)

    def __setattr__(self, key, value):
        self[key] = value

    @classmethod
    def select_all(cls, **kwargs):
        ms = mysql_singleton.Mysql().singleton()
        if kwargs:  # 当有参数传入的时候
            key = list(kwargs.keys())[0]
            value = kwargs[key]
            sql = "select * from %s where %s=?" % (cls.table_name, key)
            sql = sql.replace('?', '%s')
            re = ms.select(sql, value)
        else:  # 当无参传入的时候查询所有
            sql = "select * from %s" % cls.table_name
            re = ms.select(sql)
        return [cls(**r) for r in re]

    @classmethod
    def select_one(cls, **kwargs):
        # 此处只支持单一条件查询
        key = list(kwargs.keys())[0]
        value = kwargs[key]
        ms = mysql_singleton.Mysql().singleton()
        sql = "select * from %s where %s=?" % (cls.table_name, key)

        sql = sql.replace('?', '%s')
        re = ms.select(sql, value)
        if re:
            return cls(**re[0])
        else:
            return None

    def save(self):
        ms = mysql_singleton.Mysql().singleton()
        fields = []
        params = []
        args = []
        for k, v in self.mapping.items():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, v.default))
        sql = "insert into %s (%s) values (%s)" % (self.table_name, ','.join(fields), ','.join(params))
        sql = sql.replace('?', '%s')
        ms.execute(sql, args)

    def update(self):
        ms = mysql_singleton.Mysql().singleton()
        fields = []
        args = []
        pr = None
        for k, v in self.mapping.items():
            if v.primary_key:
                pr = getattr(self, k, v.default)
            else:
                fields.append(v.name + '=?')
                args.append(getattr(self, k, v.default))
        sql = "update %s set %s where %s = %s" % (
            self.table_name, ', '.join(fields), self.primary_key, pr)

        sql = sql.replace('?', '%s')
        print(sql)
        ms.execute(sql, args)
