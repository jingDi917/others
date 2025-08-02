from scipy.stats import gamma
from scipy.stats import poisson
from scipy.stats import binom
import math
from .common import SUM_PROB, DIFF_PROB, FIRST_FILTER_PAIR_THRESHOLD, SECOND_FILTER_PAIR_THRESHOLD, AUXILIAY_RANGE, PAIR_PROB, TUPLE_PROB, ODD_EVEN_RATIO, NUMBER, POSITION_RANGE, POSITION_RELATION, IGNORE_DIFF_THRESHOLD, IGNORE_SUM_THRESHOLD, ENHANCE_DIFF_THRESHOLD, ENHANCE_SUM_THRESHOLD
from .common import DATA_INDEX_NAME, DATA_HUNDREDS_NAME, DATA_TENS_NAME, DATA_ONES_NAME, PDF_ADD_FATOR, PDF_TIME_FACTOR, PDF_DECAL_FACTOR, FINAL_DROP_RATIO
from .common import GetBaseData
from .data_status import DataOperator
from .data_status import getSum, getDiff, getALlData, isPair, isTuple, oddEvenRatio, positionRange, positionRelations
import traceback
import json
from itertools import permutations
import random

preditct_record = {}
random.seed(42)  # 或 np.random.seed(42)

class Predictor:

    @classmethod
    def predict(cls, base_prob, data_status, data_index = None):
        try:
            next_pair = GetPair.getNextPair(base_prob, data_status)

            filter_number_map = GetBaseData.getFilterNumberMap()
            enhance_numbetr_map = GetBaseData.getEnhanceNumberMap()
            raw_data = GetBaseData.getRawData(data_index)
            if raw_data[-1:] is None or DATA_INDEX_NAME not in raw_data[-1:] or DATA_HUNDREDS_NAME not in raw_data[-1:] or DATA_TENS_NAME not in raw_data[-1:] or DATA_ONES_NAME not in raw_data[-1:]:
                raw_data = raw_data[:-1]
            real_stat_map = BsaeStrategy.getRealDateStat(raw_data)
            filter_map = FilterStrategy.getFilterMap(real_stat_map, filter_number_map)
            enhance_map = EnhanceStrategy.getEnhanceMap(real_stat_map, enhance_numbetr_map)

            predit_res, filter_res, enhance_res = cls.getPredictData(next_pair, filter_map, enhance_map, raw_data, base_prob)

            supplement_res = cls.getSupplementData(base_prob, data_status)

            merge_res = {}
            if predit_res is not None:
                merge_res.update(predit_res)
            if supplement_res is not None:
                merge_res.update(supplement_res)

            position_range_pair, position_relation_pair = GetPair.getSortPair(base_prob, data_status)
            final_res = {}
            for key, value in merge_res.items():
                hundreds = int(key[0])
                tens = int(key[1])
                ones = int(key[2])
                sort_key_position_relation = ''.join(sorted(positionRelations(hundreds, tens, ones)))
                find_flag = False
                for position_range in position_relation_pair:
                    sorted_position_range = ''.join(sorted(map(str, position_range)))
                    if sort_key_position_relation == sorted_position_range:
                        find_flag = True
                        new_hundreds, one_tens, new_ones = cls.adjustPositionOrder(hundreds, tens, ones, key, position_range)
                        final_res[f"{new_hundreds}{one_tens}{new_ones}"] = value
                        break
                if not find_flag:
                    final_res.update({key: value})

            selected_res = cls.dropElementsByRatio(final_res, FINAL_DROP_RATIO)

            return selected_res, final_res, merge_res, filter_res, enhance_res, filter_map, enhance_map, next_pair
        except Exception as e:
            err_msg = traceback.format_exc()
            raise Exception(f"预测失败: {err_msg}")
        

    @classmethod
    def dropElementsByRatio(cls, items, drop_ratio):
        """随机丢弃字典中的键值对"""
        if not 0 <= drop_ratio <= 1:
            raise ValueError("drop_ratio 必须在 [0, 1] 范围内")
        
        keys = list(items.keys())
        num_to_keep = int(len(keys) * (1 - drop_ratio))
        kept_keys = random.sample(keys, num_to_keep)
        
        return {k: items[k] for k in kept_keys}


    @classmethod
    def adjustPositionOrder(cls, hundreds, tens, ones, original_position_relation, update_position_relation):
        # 定义符号到比较关系的映射
        relation_map = {
            '<': lambda a, b: a < b,
            '>': lambda a, b: a > b,
            '=': lambda a, b: a == b,
        }
        
        # 解析当前关系 A
        a1, a2 = original_position_relation[0], original_position_relation[1]
        # 解析目标关系 B
        b1, b2 = update_position_relation[0], update_position_relation[1]
        
        # 生成所有可能的排列
        numbers = [hundreds, tens, ones]
        for perm in permutations(numbers):
            x, y, z = perm
            # 检查当前排列是否满足目标关系 B
            if (relation_map[b1](x, y) and relation_map[b2](y, z)):
                return perm
        
        # 如果没有找到满足条件的排列（理论上不会发生，因为三个数总能找到某种顺序）
        return (hundreds, tens, ones)
    
    @classmethod
    def getSupplementData(cls, base_prob, data_status):
        possible_sum = []
        sum_set = base_prob[SUM_PROB]
        sum_num_set = data_status[SUM_PROB]
        diff_set = base_prob[DIFF_PROB]
        diff_num_set = data_status[DIFF_PROB]
        pair_set = base_prob[PAIR_PROB]
        pair_num_set = data_status[PAIR_PROB]
        tuple_set = base_prob[TUPLE_PROB]
        tuple_num_set = data_status[TUPLE_PROB]
        odd_even_ratio_set = base_prob[ODD_EVEN_RATIO]
        odd_even_ratio_num_set = data_status[ODD_EVEN_RATIO]

        for key, value in sum_set.items():
            if key not in sum_num_set:
                continue
            if value * sum_num_set[key] > 1.5:
                possible_sum.append(key)

        possible_diff = []
        for key, value in diff_set.items():
            if key not in diff_num_set:
                continue
            if value * diff_num_set[key] > 1.7:
                possible_diff.append(key)

        other_supplement_flag = pair_set * pair_num_set > 2.5 and tuple_set * tuple_num_set > 2.5
        possible_odd_even_ratio = []
        for key, value in odd_even_ratio_set.items():
            if key not in odd_even_ratio_num_set:
                continue
            if value * odd_even_ratio_num_set[key] > 2.5:
                possible_odd_even_ratio.append(key)
        
        supplement_res = {}
        raw_set3d, nor_set3d = getALlData()
        for i, j, k in nor_set3d:
            sum_value = str(getSum(i, j, k))
            diff_value = str(getDiff(i, j, k))   
            odd_even_ratio_value = oddEvenRatio(i, j, k)
            if sum_value in possible_sum and diff_value in possible_diff:
                supplement_res[f"{i}{j}{k}"] = 1
                continue
            # if other_supplement_flag and odd_even_ratio_value in possible_odd_even_ratio:
            #     supplement_res[f"{i}{j}{k}"] = 1
            #     continue
                

        return supplement_res
    
    @classmethod
    def getPredictData(cls, next_pair, filter_map, enhance_map, recent_ans, base_prob):
        raw_set3d, nor_set3d = getALlData()
        final_res = {}
        filter_res = {}
        enhance_res = {}
        for i, j, k in nor_set3d:
            filter_falg = cls.isFilter(i, j, k, filter_map, recent_ans, base_prob)
            enhance_flag = cls.isEnhance(i, j, k, enhance_map, recent_ans, base_prob)
            sum_value = getSum(i, j, k)
            diff_value = getDiff(i, j, k)       
            key = f"{sum_value}\t{diff_value}"
            if key in next_pair:
                if enhance_flag != 0:
                    final_res[f"{i}{j}{k}"] = 2
                    enhance_res[f"{i}{j}{k}"] = enhance_flag
                    continue
                if filter_falg != 0:
                    filter_res[f"{i}{j}{k}"] = filter_falg
                    continue
                if next_pair[key] > SECOND_FILTER_PAIR_THRESHOLD:
                    final_res[f"{i}{j}{k}"] = 1
                    continue
                filter_res[f"{i}{j}{k}"] = 10
            else:
                filter_res[f"{i}{j}{k}"] = 100
        return final_res, filter_res, enhance_res
    
    @classmethod
    def getRecentPairFlag(cls, recent_ans):
        if len(recent_ans) < 2:
            return False
        pre_record = recent_ans[-1:][0]
        return isPair(int(pre_record[DATA_HUNDREDS_NAME]), int(pre_record[DATA_TENS_NAME]), int(pre_record[DATA_ONES_NAME]))
    

    @classmethod
    def getRecentPositionRange(cls, recent_ans):
        if not recent_ans:
            return []
        recent_position_range_list = []
        for record in recent_ans[-3:]:
            hundreds = int(record[DATA_HUNDREDS_NAME])
            tens = int(record[DATA_TENS_NAME])
            ones = int(record[DATA_ONES_NAME])
            recent_position_range_list.append(positionRange(hundreds, tens, ones))
        return recent_position_range_list

    
    @classmethod
    def isFilter(cls, i, j, k, filter_map, recent_ans, base_prob):
        if not filter_map:
            return 0
        sum_value = str(getSum(i, j ,k))
        diff_value = str(getDiff(i, j ,k))
        pair_flag = isPair(i, j, k)
        recent_pair_falg = cls.getRecentPairFlag(recent_ans)
        tuple_flag = isTuple(i, j, k)
        odd_even_value = oddEvenRatio(i, j, k)
        position_range_value = positionRange(i, j, k)
        recent_postion_range_list = cls.getRecentPositionRange(recent_ans)
        position_relation_value = positionRelations(i, j, k)
        if SUM_PROB in base_prob and sum_value in base_prob[SUM_PROB] and base_prob[SUM_PROB][sum_value] < IGNORE_SUM_THRESHOLD:
            if "1" not in preditct_record:
                preditct_record["1"] = 0
            preditct_record["1"] += 1
            return 1
        if DIFF_PROB in base_prob and diff_value in base_prob[DIFF_PROB] and base_prob[DIFF_PROB][diff_value] < IGNORE_DIFF_THRESHOLD:
            if "2" not in preditct_record:
                preditct_record["2"] = 0
            preditct_record["2"] += 1
            return 2
        
        sum_set_flag = SUM_PROB in filter_map and sum_value in filter_map[SUM_PROB]
        diff_set_flag = DIFF_PROB in filter_map and diff_value in filter_map[DIFF_PROB]
        odd_even_set_flag = ODD_EVEN_RATIO in filter_map and odd_even_value in filter_map[ODD_EVEN_RATIO]
        pair_set_flag = (PAIR_PROB in filter_map and pair_flag) or recent_pair_falg
        tuple_set_flag = TUPLE_PROB in filter_map and tuple_flag
        position_range_flag = position_range_value in recent_postion_range_list
        auxiliary_set_num = 0
        auxiliary_set_num += odd_even_set_flag
        auxiliary_set_num += pair_set_flag
        auxiliary_set_num += tuple_set_flag
        auxiliary_set_num += position_range_flag
        if sum_set_flag and diff_set_flag:
            if "3" not in preditct_record:
                preditct_record["3"] = 0
            preditct_record["3"] += 1
            return 3
        if (sum_set_flag or diff_set_flag) and auxiliary_set_num >= 1:
            if "4" not in preditct_record:
                preditct_record["4"] = 0
            preditct_record["4"] += 1
            return 4
        if auxiliary_set_num >= 3:
            if "5" not in preditct_record:
                preditct_record["5"] = 0
            preditct_record["5"] += 1
            return 5
        # if SUM_PROB in filter_map and sum_value in filter_map[SUM_PROB]:
        #     if "3" not in preditct_record:
        #         preditct_record["3"] = 0
        #     preditct_record["3"] += 1
        #     return 3
        # if DIFF_PROB in filter_map and diff_value in filter_map[DIFF_PROB]:
        #     if "4" not in preditct_record:
        #         preditct_record["4"] = 0
        #     preditct_record["4"] += 1
        #     return 4
        # if ODD_EVEN_RATIO in filter_map and odd_even_value in filter_map[ODD_EVEN_RATIO]:
        #     if "5" not in preditct_record:
        #         preditct_record["5"] = 0
        #     preditct_record["5"] += 1
        #     return 5
        # if (PAIR_PROB in filter_map and filter_map[PAIR_PROB] and pair_flag):
        #     if "6" not in preditct_record:
        #         preditct_record["6"] = 0
        #     preditct_record["6"] += 1
        #     return 6
        # if TUPLE_PROB in filter_map and filter_map[TUPLE_PROB] and tuple_flag:
        #     if "7" not in preditct_record:
        #         preditct_record["7"] = 0
        #     preditct_record["7"] += 1
        #     return 7
        return 0
    
    @classmethod
    def isEnhance(cls, i, j, k, enhance_map, recent_ans, base_prob):
        if not enhance_map:
            return 0
        sum_value = str(getSum(i, j ,k))
        diff_value = str(getDiff(i, j ,k))
        pair_flag = isPair(i, j, k)
        tuple_flag = isTuple(i, j, k)
        odd_even_value = oddEvenRatio(i, j, k)
        position_range = positionRange(i, j, k)
        position_relation = positionRelations(i, j, k)

        num_set_flag = NUMBER in enhance_map and (i in enhance_map[NUMBER] or j in enhance_map[NUMBER] or k in enhance_map[NUMBER])
        sum_set_flag = SUM_PROB in enhance_map and sum_value in enhance_map[SUM_PROB]
        diff_set_flag = DIFF_PROB in enhance_map and diff_value in enhance_map[DIFF_PROB]
        tuple_set_flag = TUPLE_PROB in enhance_map and enhance_map[TUPLE_PROB] and tuple_flag
        odd_even_set_flag = ODD_EVEN_RATIO in enhance_map and odd_even_value in enhance_map[ODD_EVEN_RATIO]
        pair_set_flag = PAIR_PROB in enhance_map and enhance_map[PAIR_PROB] and pair_flag

        auxiliary_flag_num = 0
        auxiliary_flag_num += num_set_flag
        auxiliary_flag_num += tuple_set_flag
        auxiliary_flag_num += odd_even_set_flag
        auxiliary_flag_num += pair_set_flag
        if sum_set_flag and diff_set_flag:
            return 1
        if (sum_set_flag or diff_set_flag) and auxiliary_flag_num >= 2:
            return 2
        if auxiliary_flag_num > 3:
            return 3
        # if odd_even_set_flag and pair_set_flag:
        #     return 4
        # if odd_even_set_flag and tuple_set_flag:
        #     return 5
        # if SUM_PROB in enhance_map and sum_value in enhance_map[SUM_PROB]:
        #     return 1
        # if DIFF_PROB in enhance_map and diff_value in enhance_map[DIFF_PROB]:
        #     return 2
        # if ODD_EVEN_RATIO in enhance_map and odd_even_value in enhance_map[ODD_EVEN_RATIO]:
        #     return 3
        # if PAIR_PROB in enhance_map and enhance_map[PAIR_PROB] and pair_flag:
        #     return 4
        # if TUPLE_PROB in enhance_map and enhance_map[TUPLE_PROB] and tuple_flag:
        #     return 5
        return 0

class CalulateMathProbability:
    @classmethod
    def getKthEvegntProbByGamma(cls, prob, k, t):
        """
        计算在时间 t 之前，事件第 k 次发生的概率。
        prob: 事件发生率（泊松过程的 λ）。
        k: 第 k 次事件。
        t: 时间长度。
        """
        return gamma.cdf(t, k, scale=1/prob)
    
    @classmethod
    def getKthEvegntProbByPoisson(cls, prob, k, t):
        """
        计算在时间 t 之前，事件第 k 次发生的概率。
        prob: 事件发生率（泊松过程的 λ）。
        k: 第 k 次事件。
        t: 时间长度。
        """
        return poisson.sf(k - 1, prob * t)  # P(N(t) >= k)
    
    @classmethod
    def getKthEvegntProbByBinomial(cls, prob, k, t):
        """
        计算在时间 t 之前，事件第 k 次发生的概率。
        prob: 事件发生率（泊松过程的 λ）。
        k: 第 k 次事件。
        t: 时间长度。
        """
        return binom.sf(k, t, prob)
    
    @classmethod
    def getKthEventProbNew(cls, prob, k, t):
        """
        计算在时间 t 之前，事件第 k 次发生的概率。
        prob: 事件发生率（泊松过程的 λ）。
        k: 第 k 次事件。
        t: 时间长度。
        """
        return cls.getKthEvegntProbByPoisson(prob, k, t) #+ (prob + PDF_ADD_FATOR) * min(PDF_TIME_FACTOR, PDF_DECAL_FACTOR * t) / PDF_DECAL_FACTOR / t
class GetPair:

    @classmethod
    def getNextPair(cls, base_prob, data_status):
        next_pdf = cls.getNextPdf(base_prob, data_status)
        if SUM_PROB not in next_pdf or DIFF_PROB not in next_pdf:
            return []
        
        next_pair = {}
        sum_set = next_pdf[SUM_PROB]
        diff_set = next_pdf[DIFF_PROB]
        for s_key, s_value in sum_set.items():
            for d_key, d_value in diff_set.items():
                prob = s_value * d_value
                if prob < FIRST_FILTER_PAIR_THRESHOLD:
                    continue
                next_pair[f"{s_key}\t{d_key}"] = prob
        return next_pair
    
    @classmethod
    def getNextPdf(cls, base_prob, data_status):
        if isinstance(base_prob, float) and isinstance(data_status, int):
            return CalulateMathProbability.getKthEventProbNew(base_prob, 1, data_status)
        prob_map = {}
        for key in data_status:
            if key not in base_prob:
                continue
            prob_map[key] = cls.getNextPdf(base_prob[key], data_status[key])

        return prob_map
    
    @classmethod
    def getSortPair(cls, base_prob, data_status):
        next_pdf = cls.getNextPdf(base_prob, data_status)
        if POSITION_RANGE not in next_pdf or POSITION_RELATION not in next_pdf:
            return []
        
        position_range_set = next_pdf[POSITION_RANGE]
        position_relation_set = next_pdf[POSITION_RELATION]
        position_range_res = sorted(position_range_set.items(), key=lambda x: x[1], reverse=True)
        position_relation_res = sorted(position_relation_set.items(), key=lambda x: x[1], reverse=True)
        return position_range_res, position_relation_res

class BsaeStrategy:
    @classmethod
    def initRealDataStat(cls):
        try:
            # 初始化基础概率
            base_map = GetBaseData.getBaseProb()
            real_data_stat = {}
            for key in base_map.keys():
                if isinstance(base_map[key], dict):
                    real_data_stat[key] = {k: 0 for k, v in base_map[key].items()}
                else:
                    real_data_stat[key] = 0
            return real_data_stat
        except Exception as e:
            raise Exception(f"初始化数据失败: {e}")
    
    
    @classmethod
    def getRealDateStat(cls, raw_data):
        if not raw_data:
            return None

        stat_data = raw_data[-AUXILIAY_RANGE:]
        real_data_stat_map = cls.initRealDataStat()
        for record in stat_data:
            DataOperator.updateDataStatistic(record, real_data_stat_map)

        return real_data_stat_map   
class FilterStrategy(BsaeStrategy):

    @classmethod
    def getFilterMap(cls, real_data_stat_map, filter_map):
        if not real_data_stat_map or not filter_map:
            return {}
        num_filter_key = cls.getFilterFromDict(real_data_stat_map, filter_map, NUMBER)
        sum_filter_key = cls.getFilterFromDict(real_data_stat_map, filter_map, SUM_PROB)
        diff_filter_key = cls.getFilterFromDict(real_data_stat_map, filter_map, DIFF_PROB)
        pair_filter_key = cls.getFilterFromSingle(real_data_stat_map, filter_map, PAIR_PROB)
        tuple_filter_key = cls.getFilterFromSingle(real_data_stat_map, filter_map, TUPLE_PROB)
        odd_even_filter_key = cls.getFilterFromDict(real_data_stat_map, filter_map, ODD_EVEN_RATIO)
        pos_range_filter_key = cls.getFilterFromDict(real_data_stat_map, filter_map, POSITION_RANGE)
        pos_relation_filter_key = cls.getFilterFromDict(real_data_stat_map, filter_map, POSITION_RELATION)

        return {
            NUMBER: num_filter_key,
            SUM_PROB: sum_filter_key,
            DIFF_PROB: diff_filter_key,
            PAIR_PROB: pair_filter_key,
            TUPLE_PROB: tuple_filter_key,
            ODD_EVEN_RATIO: odd_even_filter_key,
            POSITION_RANGE: pos_range_filter_key,
            POSITION_RELATION: pos_relation_filter_key
        }

    @classmethod
    def getFilterFromDict(cls, real_data_stat_map, filter_map, name):
        if not real_data_stat_map or not filter_map:
            return []
        if name not in real_data_stat_map or name not in filter_map:
            return []
        if real_data_stat_map[name] is None or filter_map[name] is None:
            return []
        stat_num_map = real_data_stat_map[name]
        filter_num_map = filter_map[name]
        if name == NUMBER:
            filter_num_map = {key: value * 3 for key, value in filter_num_map.items()}
        filter_key = []
        for key, stat_num in stat_num_map.items():
            if key not in filter_num_map:
                continue
            if stat_num >= filter_num_map[key]:
                filter_key.append(key)
        return filter_key

    @classmethod
    def getFilterFromSingle(cls, real_data_stat_map, filter_map, name):
        if not real_data_stat_map or not filter_map:
            return False
        if name not in real_data_stat_map or name not in filter_map:
            return False
        if real_data_stat_map[name] is None or filter_map[name] is None:
            return False
        stat_num = real_data_stat_map[name]
        filter_num = filter_map[name]
        if stat_num >= filter_num:
            return True
        return False
    
class EnhanceStrategy(BsaeStrategy):
    @classmethod
    def getEnhanceMap(cls, real_data_stat_map, enhance_map):
        if not real_data_stat_map or not enhance_map:
            return {}
        num_filter_key = cls.getEnhanceFromDict(real_data_stat_map, enhance_map, NUMBER)
        sum_filter_key = cls.getEnhanceFromDict(real_data_stat_map, enhance_map, SUM_PROB)
        diff_filter_key = cls.getEnhanceFromDict(real_data_stat_map, enhance_map, DIFF_PROB)
        pair_filter_key = cls.getEnhanceFromSingle(real_data_stat_map, enhance_map, PAIR_PROB)
        tuple_filter_key = cls.getEnhanceFromSingle(real_data_stat_map, enhance_map, TUPLE_PROB)
        odd_even_filter_key = cls.getEnhanceFromDict(real_data_stat_map, enhance_map, ODD_EVEN_RATIO)
        pos_range_filter_key = cls.getEnhanceFromDict(real_data_stat_map, enhance_map, POSITION_RANGE)
        pos_relation_filter_key = cls.getEnhanceFromDict(real_data_stat_map, enhance_map, POSITION_RELATION)

        return {
            NUMBER: num_filter_key,
            SUM_PROB: sum_filter_key,
            DIFF_PROB: diff_filter_key,
            PAIR_PROB: pair_filter_key,
            TUPLE_PROB: tuple_filter_key,
            ODD_EVEN_RATIO: odd_even_filter_key,
            POSITION_RANGE: pos_range_filter_key,
            POSITION_RELATION: pos_relation_filter_key
        }

    @classmethod
    def getEnhanceFromDict(cls, real_data_stat_map, enhance_map, name):
        if not real_data_stat_map or not enhance_map:
            return []
        if name not in real_data_stat_map or name not in enhance_map:
            return []
        if real_data_stat_map[name] is None or enhance_map[name] is None:
            return []
        stat_num_map = real_data_stat_map[name]
        enhance_num_map = enhance_map[name]
        if name == NUMBER:
            enhance_num_map = {key: value * 3 for key, value in enhance_num_map.items()}
        filter_key = []
        for key, stat_num in stat_num_map.items():
            if key not in enhance_num_map:
                continue
            if stat_num < enhance_num_map[key]:
                filter_key.append(key)
        return filter_key

    @classmethod
    def getEnhanceFromSingle(cls, real_data_stat_map, enhance_map, name):
        if not real_data_stat_map or not enhance_map:
            return False
        if name not in real_data_stat_map or name not in enhance_map:
            return False
        if real_data_stat_map[name] is None or enhance_map[name] is None:
            return False
        stat_num = real_data_stat_map[name]
        enhance_num = enhance_map[name]
        if stat_num < enhance_num:
            return True
        return False



if __name__ == '__main__':
    # 计算
    print(CalulateMathProbability.getKthEventProbNew(0.04545454545454545, 4, 100))
    # filter 策略
    # filter_number_map = GetBaseData.getFilterNumberMap()
    # enhance_numbetr_map = GetBaseData.getEnhanceNumberMap()
    # account_array = GetBaseData.getAccounts()
    # current_year, current_index = account_array[1]
    # data_index = f"{current_year}{current_index}"
    # raw_data = GetBaseData.getRawData(data_index)
    # real_stat_map = FilterStrategy.getRealDateStat(raw_data)
    # filter_map = FilterStrategy.getFilterMap(real_stat_map, filter_number_map)
    # enhance_map = EnhanceStrategy.getEnhanceMap(real_stat_map, enhance_numbetr_map)
    # print(filter_map)
    # print(enhance_map)
    # 预测
    # base_prob = GetBaseData.getBaseProb()
    # data_status = GetBaseData.getDataStatus()
    # account_array = GetBaseData.getAccounts()
    # current_year, current_index = account_array[1]
    # data_index = f"{current_year}{current_index}"

    # final_res, filter_map, enhance_map, next_pair = Predictor.predict(base_prob, data_status, data_index)
    # print(f"len: {len(final_res)}")
    # print(json.dumps(final_res, ensure_ascii=False))
    # print(json.dumps(filter_map, ensure_ascii=False))
    # print(json.dumps(enhance_map, ensure_ascii=False))
    #print(json.dumps(next_pair, ensure_ascii=False))
