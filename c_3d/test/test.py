from ..scripts.strategy import Predictor, BsaeStrategy, preditct_record
from ..scripts.common import BaseCommonFunc, DATA_INDEX_NAME, DATA_HUNDREDS_NAME, DATA_TENS_NAME, DATA_ONES_NAME
from ..scripts.common import GetBaseData, WriteBaseData
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
    for i in range(index, min(index + 500, len(raw_data))):
        if i >= len(raw_data):
            break
        try:
            record = raw_data[i]
            index = record[DATA_INDEX_NAME]
            hundred = int(record[DATA_HUNDREDS_NAME])
            ten = int(record[DATA_TENS_NAME])
            one = int(record[DATA_ONES_NAME])

            final_res, all_res, merge_res, filter_res, enhance_res, _, _, _ = Predictor.predict(base_prob, data_status, index)
            originResStr = f"{hundred}{ten}{one}"
            normalResStr = getNormalSet(hundred, ten, one)
            pair_flag = isPair(hundred, ten, one)
            if len(final_res) != 0:
                total += 1
            if normalResStr in merge_res:
                if originResStr in final_res:
                    receive += 1040 * merge_res[normalResStr]
                elif pair_flag:
                    receive += 346 * merge_res[normalResStr]
                else:
                    receive += 173 * merge_res[normalResStr]
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


def test():
    raw_data = GetBaseData.getRawData()
    index = 0
    for record in raw_data:
        if record[DATA_INDEX_NAME] == '2025079':
            break
        index += 1
    pre_data = raw_data[0:index]
    after_data = raw_data[index:]
    array_index = index
    pre_data.append({
        DATA_INDEX_NAME: '2025079',
        DATA_HUNDREDS_NAME: '6',
        DATA_TENS_NAME: '5',
        DATA_ONES_NAME: '7'
    })
    pre_data.append({
        DATA_INDEX_NAME: '2025080',
        DATA_HUNDREDS_NAME: '5',
        DATA_TENS_NAME: '0',
        DATA_ONES_NAME: '0'
    })
    for record in after_data:
        data_index = record[DATA_INDEX_NAME]
        if data_index == '':
            pre_data.append(record)
            continue
        current_year, current_index = BaseCommonFunc.splitDataIndex(data_index)
        current_year, current_index = BaseCommonFunc.addIndex(current_year, current_index)
        current_year, current_index = BaseCommonFunc.addIndex(current_year, current_index)
        new_data_index = f"{current_year}{current_index:03d}"
        record[DATA_INDEX_NAME] = new_data_index
        pre_data.append(record)
    raw_datas = []
    for record in pre_data:
        epoch_index = record[DATA_INDEX_NAME]
        if epoch_index == "":
            continue
        hundreds = record[DATA_HUNDREDS_NAME]
        tens = record[DATA_TENS_NAME]
        ones = record[DATA_ONES_NAME]
        raw_datas.append(f"{epoch_index}\t{hundreds}\t{tens}\t{ones}\n")
    WriteBaseData.writeAllRawData(raw_datas)
    

if __name__ == '__main__':

    hit, total, sum_res, receive, pay = main()
    print(f"hit:{hit}, total:{total}, sum_res:{sum_res}, receive:{receive}, pay:{pay}, hit ratio:{hit/total}, average:{sum_res/total}")
    #print(json.dumps(preditct_record, ensure_ascii=False))

    #test()

    # row_data = GetBaseData.getRawData()
    # length = len(row_data)
    # random_number = random.randint(100, length-100)  # 包含 i 和 j
    # selected_data = row_data[random_number:random_number+100]
    # stat_map = BsaeStrategy.getRealDateStat(selected_data)
    # print(json.dumps(stat_map,ensure_ascii=False))