
from .common import DATA_INDEX_NAME, DATA_HUNDREDS_NAME, DATA_TENS_NAME, DATA_ONES_NAME
from .common import PAIR_PROB, TUPLE_PROB, ODD_EVEN_RATIO, SUM_PROB, DIFF_PROB, NUMBER, POSITION_RANGE, POSITION_RELATION
import traceback

# 获取原始数据集    
def getALlData():
    def getTupleSet(i,j,k):
        arr = [i,j,k]
        arr.sort()
        return tuple(arr)
    raw_set3d = set()
    nor_set3d = set()
    for i in range(0,10):
        for j in range(0,10):
            for k in range(0,10):
                nor_set3d.add(getTupleSet(i,j,k))
                raw_set3d.add((i, j, k))
    return raw_set3d, nor_set3d

# 数据判断
def oddEvenRatio(i,j,k):
    odd = 0
    even = 0
    if i % 2 == 0:
        even += 1
    else:
        odd += 1
    if j % 2 == 0:
        even += 1
    else:
        odd += 1
    if k % 2 == 0:  
        even += 1
    else:
        odd += 1
    return f"{odd}-{even}"

tupleSet = [(0,9),(1,8),(2,7),(3,6),(4,5)]
def isTuple(i,j,k):
    arr = [i,j,k]
    arr.sort()
    is_tuple = False
    for t in tupleSet:
        tmoFlag = True
        for num in list(t):
            if num not in arr:
                tmoFlag = False
                break
        if tmoFlag:
            is_tuple = True
            break
    return is_tuple

def isPair(i,j,k):
    return i == j or j == k or i == k

def getDiff(i,j,k):
    return max(abs(i - j),max(abs(j - k), abs(k - i)))

def getSum(i,j,k):
    return i + j + k

def calRelatio(i, j):
    if i > j:
        return '>'
    elif i < j:
        return '<'
    return '='
def positionRelations(i, j, k):
    res = calRelatio(i, j)
    res += calRelatio(j, k)
    return res

number_range = {
    's': [0, 1, 2],
    'm': [3, 4, 5, 6],
    'l': [7, 8, 9]
}
def calRange(i):
    for key, value in number_range.items():
        if i in value:
            return key
    return 'u'
def positionRange(i, j, k):
    res = calRange(i)
    res += calRange(j)
    res += calRange(k)
    return res



# 更新数据状态

class DataOperator:
    @classmethod
    def updateRtDataStatus(cls, record, data_status: dict, base_prob: dict):
        try:
            # 自增
            for key in data_status.keys():
                if isinstance(data_status[key], dict):
                    for sub_key in data_status[key].keys():
                        data_status[key][sub_key] += 1
                else:
                    data_status[key] += 1

            # 复位
            prob_map_res = {}
            data_index = record[DATA_INDEX_NAME]
            hundreds = int(record[DATA_HUNDREDS_NAME])
            tens = int(record[DATA_TENS_NAME])
            ones = int(record[DATA_ONES_NAME])
            sum_value = getSum(hundreds, tens, ones)
            diff_value = getDiff(hundreds, tens, ones)
            odd_even_ratio = oddEvenRatio(hundreds, tens, ones)
            position_range = positionRange(hundreds, tens, ones)
            position_rel = positionRelations(hundreds, tens, ones)
            if NUMBER in data_status:
                data_status[NUMBER][str(hundreds)] = 1
                data_status[NUMBER][str(tens)] = 1
                data_status[NUMBER][str(ones)] = 1
                prob_map_res[NUMBER] = {str(hundreds): base_prob[NUMBER][str(hundreds)], str(tens): base_prob[NUMBER][str(tens)], str(ones): base_prob[NUMBER][str(ones)]}
            if SUM_PROB in data_status:
                data_status[SUM_PROB][str(sum_value)] = 1
                prob_map_res[SUM_PROB] = {str(sum_value): base_prob[SUM_PROB][str(sum_value)]}
            if DIFF_PROB in data_status:
                data_status[DIFF_PROB][str(diff_value)] = 1
                prob_map_res[DIFF_PROB] = {str(diff_value): base_prob[DIFF_PROB][str(diff_value)]}
            if PAIR_PROB in data_status and isPair(hundreds, tens, ones):
                data_status[PAIR_PROB] = 1
                prob_map_res[PAIR_PROB] = base_prob[PAIR_PROB]
            if TUPLE_PROB in data_status and isTuple(hundreds, tens, ones):
                data_status[TUPLE_PROB] = 1
                prob_map_res[TUPLE_PROB] = base_prob[TUPLE_PROB]
            if ODD_EVEN_RATIO in data_status:
                data_status[ODD_EVEN_RATIO][odd_even_ratio] = 1
                prob_map_res[ODD_EVEN_RATIO] = {str(odd_even_ratio): base_prob[ODD_EVEN_RATIO][str(odd_even_ratio)]}
            if POSITION_RANGE in data_status:
                data_status[POSITION_RANGE][position_range] = 1
                prob_map_res[POSITION_RANGE] = {str(position_range): base_prob[POSITION_RANGE][str(position_range)]}
            if POSITION_RELATION in data_status:
                data_status[POSITION_RELATION][position_rel] = 1
                prob_map_res[POSITION_RELATION] = {str(position_rel): base_prob[POSITION_RELATION][str(position_rel)]}
            return prob_map_res
        except Exception as e:
            err_msg = traceback.format_exc()
            raise Exception(f"更新数据状态: {record}, 错误信息: {err_msg}")
        
    @classmethod
    def updateDataStatistic(cls, record, statistic_map: dict):
        try:
            # 复位
            # 更新数据统计
            data_index = record[DATA_INDEX_NAME]
            hundreds = int(record[DATA_HUNDREDS_NAME])
            tens = int(record[DATA_TENS_NAME])
            ones = int(record[DATA_ONES_NAME])
            sum_value = getSum(hundreds, tens, ones)
            diff_value = getDiff(hundreds, tens, ones)
            odd_even_ratio = oddEvenRatio(hundreds, tens, ones)
            position_range = positionRange(hundreds, tens, ones)
            position_rel = positionRelations(hundreds, tens, ones)
            if NUMBER in statistic_map:
                statistic_map[NUMBER][str(hundreds)] += 1
                statistic_map[NUMBER][str(tens)] += 1
                statistic_map[NUMBER][str(ones)] += 1
            if SUM_PROB in statistic_map:
                statistic_map[SUM_PROB][str(sum_value)] += 1
            if DIFF_PROB in statistic_map:
                statistic_map[DIFF_PROB][str(diff_value)] += 1
            if PAIR_PROB in statistic_map and isPair(hundreds, tens, ones):
                statistic_map[PAIR_PROB] += 0
            if TUPLE_PROB in statistic_map and isTuple(hundreds, tens, ones):
                statistic_map[TUPLE_PROB] += 0
            if ODD_EVEN_RATIO in statistic_map:
                statistic_map[ODD_EVEN_RATIO][odd_even_ratio] += 1
            if POSITION_RANGE in statistic_map:
                statistic_map[POSITION_RANGE][position_range] += 1
            if POSITION_RELATION in statistic_map:
                statistic_map[POSITION_RELATION][position_rel] += 1

        except Exception as e:
            err_msg = traceback.format_exc()
            raise Exception(f"更新数据状态: {record}, 错误信息: {err_msg}")