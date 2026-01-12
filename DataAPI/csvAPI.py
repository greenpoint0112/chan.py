import os

from Common.CEnum import DATA_FIELD, KL_TYPE
from Common.ChanException import CChanException, ErrCode
from Common.CTime import CTime
from Common.func_util import str2float
from KLine.KLine_Unit import CKLine_Unit

from .CommonStockAPI import CCommonStockApi


def create_item_dict(data, column_name):
    for i in range(len(data)):
        data[i] = parse_time_column(data[i]) if column_name[i] == DATA_FIELD.FIELD_TIME else str2float(data[i])
    return dict(zip(column_name, data))


def parse_time_column(inp):
    # 支持多种时间格式：
    # 20210902113000000 (17位)
    # 2021-09-13 (10位)
    # 2021-09-13 09:30 (16位) - 新增美股分钟数据格式
    if len(inp) == 10:
        # 2021-09-13
        year = int(inp[:4])
        month = int(inp[5:7])
        day = int(inp[8:10])
        hour = minute = 0
    elif len(inp) == 16:
        # 2021-09-13 09:30
        year = int(inp[:4])
        month = int(inp[5:7])
        day = int(inp[8:10])
        hour = int(inp[11:13])
        minute = int(inp[14:16])
    elif len(inp) == 17:
        # 20210902113000000
        year = int(inp[:4])
        month = int(inp[4:6])
        day = int(inp[6:8])
        hour = int(inp[8:10])
        minute = int(inp[10:12])
    elif len(inp) == 19:
        # 其他可能的格式
        year = int(inp[:4])
        month = int(inp[5:7])
        day = int(inp[8:10])
        hour = int(inp[11:13])
        minute = int(inp[14:16])
    else:
        raise Exception(f"unknown time column from csv:{inp} (length: {len(inp)})")
    return CTime(year, month, day, hour, minute)


class CSV_API(CCommonStockApi):
    def __init__(self, code, k_type=KL_TYPE.K_DAY, begin_date=None, end_date=None, autype=None):
        self.headers_exist = True  # 第一行是否是标题，如果是数据，设置为False
        self.columns = [
            DATA_FIELD.FIELD_TIME,
            DATA_FIELD.FIELD_OPEN,
            DATA_FIELD.FIELD_HIGH,
            DATA_FIELD.FIELD_LOW,
            DATA_FIELD.FIELD_CLOSE,
            DATA_FIELD.FIELD_VOLUME,
            DATA_FIELD.FIELD_TURNOVER,
            DATA_FIELD.FIELD_TURNRATE,
        ]  # 每一列字段

        # 转换日期字符串为CTime对象以便比较
        if begin_date:
            begin_date = parse_time_column(begin_date) if isinstance(begin_date, str) else begin_date
        if end_date:
            end_date = parse_time_column(end_date) if isinstance(end_date, str) else end_date
        self.time_column_idx = self.columns.index(DATA_FIELD.FIELD_TIME)
        super(CSV_API, self).__init__(code, k_type, begin_date, end_date, autype)

    def get_kl_data(self):
        cur_path = os.path.dirname(os.path.realpath(__file__))
        k_type_name = self.k_type.name

        # 处理文件名格式映射
        # K_DAY -> day, K_5M -> 5m, K_1M -> 1m, etc.
        if k_type_name == 'K_DAY':
            freq_name = 'day'
        elif k_type_name.startswith('K_') and k_type_name.endswith('M'):
            # K_5M -> 5m, K_1M -> 1m, etc.
            minutes = k_type_name[2:-1]  # 提取数字部分
            freq_name = f"{minutes}m"
        else:
            # 其他情况，使用原来的逻辑
            freq_name = k_type_name[2:].lower()
            if freq_name.startswith('_'):
                freq_name = freq_name[1:]

        # 构建正确的文件路径 (DataAPI目录下的文件)
        file_path = os.path.join(cur_path, f"{self.code}_{freq_name}.csv")
        if not os.path.exists(file_path):
            raise CChanException(f"file not exist: {file_path}", ErrCode.SRC_DATA_NOT_FOUND)

        for line_number, line in enumerate(open(file_path, 'r')):
            if self.headers_exist and line_number == 0:
                continue
            data = line.strip("\n").split(",")
            if len(data) != len(self.columns):
                raise CChanException(f"file format error: {file_path}", ErrCode.SRC_DATA_FORMAT_ERROR)

            # 创建数据字典并解析时间
            item_dict = create_item_dict(data, self.columns)
            parsed_time = item_dict[DATA_FIELD.FIELD_TIME]

            # 时间过滤 (使用解析后的时间对象)
            if self.begin_date is not None and parsed_time < self.begin_date:
                continue
            if self.end_date is not None and parsed_time > self.end_date:
                continue
            yield CKLine_Unit(item_dict)

    def SetBasciInfo(self):
        pass

    @classmethod
    def do_init(cls):
        pass

    @classmethod
    def do_close(cls):
        pass
