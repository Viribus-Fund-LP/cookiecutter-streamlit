import re
from urllib.parse import quote, quote_plus
from uuid import uuid4

import pandas as pd
import snowflake.connector
from dotenv import dotenv_values
from snowflake.connector.compat import IS_STR
from snowflake.connector.pandas_tools import write_pandas


def _rfc_1738_quote(text):
    return re.sub(r"[:@/]", lambda m: "%%%X" % ord(m.group(0)), text)


def _quote_password(text):
    return quote(_rfc_1738_quote(text))


def temp_table_name(prefix="tmp", suffix="table"):
    parts = [prefix, str(uuid4()).replace("-", ""), suffix]
    return "_".join([str(x) for x in parts if x]).upper()


def URL(**db_parameters):
    specified_parameters = []
    if "account" not in db_parameters:
        raise Exception("account parameter must be specified.")
    if "host" in db_parameters:
        ret = "snowflake://{user}:{password}@{host}:{port}/".format(
            user=db_parameters.get("user", ""),
            password=_quote_password(db_parameters.get("password", "")),
            host=db_parameters["host"],
            port=db_parameters["port"] if "port" in db_parameters else 443,
        )
        specified_parameters += ["user", "password", "host", "port"]
    elif "region" not in db_parameters:
        ret = "snowflake://{user}:{password}@{account}/".format(
            account=db_parameters["account"],
            user=db_parameters.get("user", ""),
            password=_quote_password(db_parameters.get("password", "")),
        )
        specified_parameters += ["user", "password", "account"]
    else:
        ret = "snowflake://{user}:{password}@{account}.{region}/".format(
            account=db_parameters["account"],
            user=db_parameters.get("user", ""),
            password=_quote_password(db_parameters.get("password", "")),
            region=db_parameters["region"],
        )
        specified_parameters += ["user", "password", "account", "region"]
    if "database" in db_parameters:
        ret += quote_plus(db_parameters["database"])
        specified_parameters += ["database"]
        if "schema" in db_parameters:
            ret += "/" + quote_plus(db_parameters["schema"])
            specified_parameters += ["schema"]
    elif "schema" in db_parameters:
        raise Exception("schema cannot be specified without database")

    def sep(is_first_parameter):
        return "?" if is_first_parameter else "&"

    is_first_parameter = True
    for p in sorted(db_parameters.keys()):
        v = db_parameters[p]
        if p not in specified_parameters:
            encoded_value = quote_plus(v) if IS_STR(v) else str(v)
            ret += sep(is_first_parameter) + p + "=" + encoded_value
            is_first_parameter = False
    return ret


def connect(**kwargs):
    if not kwargs:
        kwargs = dict(
            account=dotenv_values(".env")["SNOWFLAKE_ACCOUNT"],
            user=dotenv_values(".env")["SNOWFLAKE_USER"],
            password=dotenv_values(".env")["SNOWFLAKE_PASSWORD"],
        )
    snowflake.connector.paramstyle = "numeric"
    return snowflake.connector.connect(**kwargs, client_session_keep_alive=True)


class Snowflake:
    def __init__(self, **kwargs):
        # TODO add method to refresh and/or keep alive
        self.conn = connect(**kwargs)

    def query(self, sql, **kwargs):
        cur = self.conn.cursor()
        cur.execute(sql, **kwargs)
        df = cur.fetch_pandas_all()
        df.columns = df.columns.map(str.lower)
        return df

    def execute(self, sql, **kwargs):
        return self.conn.cursor().execute(sql, **kwargs)

    def write_pandas(
        self, df, table_name, quote_identifiers=False, index=False, **kwargs
    ):
        _df = df.rename(columns=lambda x: x.upper())
        if index:
            raise NotImplementedError("Passing index=True is not supported")

        if not (
            isinstance(_df.index, pd.RangeIndex)
            and 1 == _df.index.step
            and 0 == _df.index.start
        ):
            if index:
                raise Exception(
                    "index=True and index is not RangeIndex, if you want to keep index call reset_index()"
                )
            else:
                _df = _df.reset_index(drop=True)
                _df.index = pd.RangeIndex(0, len(_df.index), 1)

        return write_pandas(
            conn=self.conn,
            df=_df,
            table_name=table_name.upper(),
            quote_identifiers=quote_identifiers,
            index=index,
            **kwargs,
        )
