from ..scripts.strategy import Predictor, BsaeStrategy, preditct_record, PredictorV2
from ..scripts.common import BaseCommonFunc, DATA_INDEX_NAME, DATA_HUNDREDS_NAME, DATA_TENS_NAME, DATA_ONES_NAME
from ..scripts.common import GetBaseData
from ..scripts.data_status import DataOperator, getSum, getDiff, isPair

import json
import random



def getCurrtentIndex(data_index, raw_data):
    index = 0
    print(data_index)
    for record in raw_data:
        if record[DATA_INDEX_NAME] == data_index:
            break
        index += 1
    return index

def getNormalSet(i,j,k):
    arr = [i,j,k]
    arr.sort()
    return ''.join(map(str, arr))  # 统一转为字符串拼接

def main():
    data_status = GetBaseData.getDataStatus()
    base_prob = GetBaseData.getBaseProb()
    account_array = GetBaseData.getAccounts()
    current_year, current_index = account_array[1]
    data_index = f"{current_year}{current_index:03d}"
    raw_data = GetBaseData.getRawData()
    index = getCurrtentIndex(data_index, raw_data)
    hit = 0
    total = 0
    sum_res = 0

    fail_map = {}
    enhance_map = {}
    receive = 0
    pay = 0
    for i in range(index, min(index + 190, len(raw_data))):
        if i >= len(raw_data):
            break
        try:
            record = raw_data[i]
            index = record[DATA_INDEX_NAME]
            hundred = int(record[DATA_HUNDREDS_NAME])
            ten = int(record[DATA_TENS_NAME])
            one = int(record[DATA_ONES_NAME])

            final_res, all_res, merge_res, filter_res, enhance_res, _, _, _ = PredictorV2.predict(base_prob, data_status, index)
            originResStr = f"{hundred}{ten}{one}"
            normalResStr = getNormalSet(hundred, ten, one)
            pair_flag = isPair(hundred, ten, one)
            if len(final_res) != 0:
                total += 1
            if originResStr in final_res:
                receive += 1040 * merge_res[normalResStr]
                hit += 1
            else:
                for _, flag in enhance_res.items():
                    if str(flag) not in enhance_map:
                        enhance_map[str(flag)] = 0
                    enhance_map[str(flag)] += 1
                if normalResStr in filter_res:
                    if str(filter_res[normalResStr]) not in fail_map:
                        fail_map[str(filter_res[normalResStr])] = 0
                    fail_map[str(filter_res[normalResStr])] += 1
                    
            sum_res += len(final_res)  
            for _, value in final_res.items():
                pay += 2 * value  
            DataOperator.updateRtDataStatus(record, data_status, base_prob)
        except Exception as e:
            print(e)


    #print(json.dumps(data_status, ensure_ascii=False))
    #final_res, _, _, _ = Predictor.predict(base_prob, data_status, data_index)
    print(json.dumps(fail_map, ensure_ascii=False))
    print(json.dumps(enhance_map, ensure_ascii=False))


    return hit, total, sum_res, receive, pay
    

if __name__ == '__main__':

    hit, total, sum_res, receive, pay = main()
    print(f"hit:{hit}, total:{total}, sum_res:{sum_res}, receive:{receive}, pay:{pay}, hit ratio:{hit/total}, average:{sum_res/total}")
    #print(json.dumps(preditct_record, ensure_ascii=False))

    # row_data = GetBaseData.getRawData()
    # length = len(row_data)
    # random_number = random.randint(100, length-100)  # 包含 i 和 j
    # selected_data = row_data[random_number:random_number+100]
    # stat_map = BsaeStrategy.getRealDateStat(selected_data)
    # print(json.dumps(stat_map,ensure_ascii=False))