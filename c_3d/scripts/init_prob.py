
from .common import BASE_PROB_FILE, FILTER_NUMBER_FILE, ENHANCE_NUMBER_FILE, PAIR_PROB, TUPLE_PROB, ODD_EVEN_RATIO, SUM_PROB, DIFF_PROB, NUMBER, POSITION_RANGE, POSITION_RELATION, AUXILIAY_RANGE, FILTER_THRESHOLD, ENHANCE_THRESHOLD, DATA_HUNDREDS_NAME, DATA_TENS_NAME, DATA_ONES_NAME
from .common import GetBaseData, WriteBaseData
from .data_status import getSum, getDiff, isPair, isTuple, oddEvenRatio, positionRelations, positionRange, getALlData
from .strategy import CalulateMathProbability
import json


class InitBaseProb:

    # 计算每个数字的概率
    @classmethod
    def getDigitProb(cls):
        most_base_prob = {}
        for num in range(0, 10):
            most_base_prob[str(num)] = 0.1
        return most_base_prob


    ## 计算和概率
    @classmethod
    def getSumProbability(cls, set3d):
        
        sumDict = {}
        sumConntDict = {}
        for i,j,k in set3d:
            sumValue = getSum(i,j,k)
            
            if sumValue not in sumDict:
                sumDict[sumValue] = 0
                sumConntDict[sumValue] = set()
            
            sumDict[sumValue] += 1
            sumConntDict[sumValue].add((i,j,k))
        all_count = len(set3d)
        return {key: value / all_count for key, value in sumDict.items()}

    ## 计算差概率
    @classmethod
    def getDiffProbability(cls, set3d):
        diffDict = {}
        diffConntDict = {}
        for i,j,k in set3d:
            diffValue = getDiff(i,j,k)
            
            if diffValue not in diffDict:
                diffDict[diffValue] = 0
                diffConntDict[diffValue] = set()
            
            diffDict[diffValue] += 1
            diffConntDict[diffValue].add((i,j,k))
        all_count = len(set3d)
        return {key: value / all_count for key, value in diffDict.items()}

    ## 计算pair
    @classmethod
    def getPair(cls, set3d):
        hitPair = 0
        all_count = len(set3d)
        for i,j,k in set3d:
            if isPair(i,j,k):
                hitPair += 1
        return hitPair / all_count

    ## 计算tuple
    @classmethod
    def getTuple(cls, set3d):


        hitTuple = 0
        all_count = len(set3d)
        for i,j,k in set3d:
            if isTuple(i,j,k):
                hitTuple += 1
        
        return hitTuple / all_count


    # 计算奇偶比
    @classmethod
    def getOddEvenRatio(cls, set3d):
        
        all_count = len(set3d)
        odd_even_ratio = {}
        for i,j,k in set3d:
            ratio = oddEvenRatio(i,j,k)
            if ratio not in odd_even_ratio:
                odd_even_ratio[ratio] = 0
            odd_even_ratio[ratio] += 1
        return  {key: value / all_count for key, value in odd_even_ratio.items()}


    # 计算大小范围
    @classmethod
    def getPositionRangeRatio(cls, set3d):
        all_count = len(set3d)
        position_range_ratio = {}
        for i, j, k in set3d:
            ratio = positionRange(i, j, k)
            if ratio not in position_range_ratio:
                position_range_ratio[ratio] = 0
            position_range_ratio[ratio] += 1
        return {key: value / all_count for key, value in position_range_ratio.items()}

    # 计算位置关系
    @classmethod
    def getPositionRelationsRatio(cls, set3d):
        all_count = len(set3d)
        position_relaton_ratio = {}
        for i, j, k in set3d:
            ratio = positionRelations(i, j, k)
            if ratio not in position_relaton_ratio:
                position_relaton_ratio[ratio] = 0
            position_relaton_ratio[ratio] += 1
        return {key: value / all_count for key, value in position_relaton_ratio.items()}
    
class InitAuxiliaryProb:

    @classmethod
    def getDictProbability(cls, name):
        base_prob = GetBaseData.getBaseProb()
        if name not in base_prob:
            return {}, {}
        sum_set = base_prob[name]
        filter_num_dict = {}
        enhance_num_dcit = {}
        for key, prob in sum_set.items():
            for i in range(0, 101):
                calProb = CalulateMathProbability.getKthEventProbNew(prob, i, 100)
                if calProb > ENHANCE_THRESHOLD:
                    enhance_num_dcit[key] = i
                if calProb < FILTER_THRESHOLD:
                    filter_num_dict[key] = i
                    break
        return filter_num_dict, enhance_num_dcit
    
    @classmethod
    def getSingleProbability(cls, name):
        base_prob = GetBaseData.getBaseProb()
        if name not in base_prob:
            return 100, 0 
        prob = base_prob[name]
        filter_num = 100
        enhance_num = 0
        for i in range(0, 101):
            calProb = CalulateMathProbability.getKthEventProbNew(prob, i, 100)
            if calProb > ENHANCE_THRESHOLD:
                enhance_num = i
            if calProb < FILTER_THRESHOLD:
                filter_num = i
                break
        return filter_num, enhance_num
    
def main(is_real_data=False, real_data = None):

    set3d = None
    if is_real_data and real_data is not None:
        set3d = set()
        for record in real_data:
            hundreds = int(record[DATA_HUNDREDS_NAME])
            tens = int(record[DATA_TENS_NAME])
            ones = int(record[DATA_ONES_NAME])
            set3d.add((hundreds, tens, ones))
    else:
        raw_set3d, nor_set3d = getALlData()
        set3d = raw_set3d
    
    
    digit_prob = InitBaseProb.getDigitProb()
    sum_prob = InitBaseProb.getSumProbability(set3d)
    diff_prob = InitBaseProb.getDiffProbability(set3d)
    pair_prob = InitBaseProb.getPair(set3d)
    tuple_prob = InitBaseProb.getTuple(set3d)
    odd_even_ratio = InitBaseProb.getOddEvenRatio(set3d)
    position_range_ratio = InitBaseProb.getPositionRangeRatio(set3d)
    position_relaton_ratio = InitBaseProb.getPositionRelationsRatio(set3d)

    # 保存到文件
    WriteBaseData.writeJsonData(BASE_PROB_FILE, {
        NUMBER: digit_prob,
        SUM_PROB: sum_prob,
        DIFF_PROB: diff_prob,
        PAIR_PROB: pair_prob,
        TUPLE_PROB: tuple_prob,
        ODD_EVEN_RATIO: odd_even_ratio,
        POSITION_RANGE: position_range_ratio,
        POSITION_RELATION: position_relaton_ratio
    })
    
    # print("概率数据已保存到", BASE_PROB_FILE)
    # print("Digit Probability:", digit_prob)
    # print(f"Sum Probability: {sum_prob}")
    # print(f"Diff Probability: {diff_prob}")
    # print(f"Pair Probability: {pair_prob}")
    # print(f"Tuple Probability: {tuple_prob}")
    # print(f"Odd Even Ratio: {odd_even_ratio}")
    # print(f"Pos Range Ratio: {position_range_ratio}")
    # print(f"Pos Relation Ratio: {position_relaton_ratio}")
    # print(f"raw_set3d Combinations: {len(raw_set3d)}")
    # print(f"nor_set3d Combinations: {len(nor_set3d)}")

    num_filter, num_enhance = InitAuxiliaryProb.getDictProbability(NUMBER)
    sum_filter_num, sum_enhance_num = InitAuxiliaryProb.getDictProbability(SUM_PROB)
    diff_filter_num, diff_enhance_num = InitAuxiliaryProb.getDictProbability(DIFF_PROB)
    pair_filter_num, pair_enhance_num = InitAuxiliaryProb.getSingleProbability(PAIR_PROB)
    tuple_filter_num, tuple_enhance_num = InitAuxiliaryProb.getSingleProbability(TUPLE_PROB)
    oe_filter_num, oe_enhance_num = InitAuxiliaryProb.getDictProbability(ODD_EVEN_RATIO)
    prange_filter_num, prange_enhance_num = InitAuxiliaryProb.getDictProbability(POSITION_RANGE)
    prel_filter_num, prel_enhance_num = InitAuxiliaryProb.getDictProbability(POSITION_RELATION)

    # 保存到文件
    WriteBaseData.writeJsonData(FILTER_NUMBER_FILE, {
        NUMBER: num_filter,
        SUM_PROB: sum_filter_num,
        DIFF_PROB: diff_filter_num,
        PAIR_PROB: pair_filter_num,
        TUPLE_PROB: tuple_filter_num,
        ODD_EVEN_RATIO: oe_filter_num,
        POSITION_RANGE: prange_filter_num,
        POSITION_RELATION: prel_filter_num
    })
    
    # print("概率数据已保存到", FILTER_NUMBER_FILE)
    # print(f"Sum Filter Number: {sum_filter_num}")
    # print(f"Diff Filter Number: {diff_filter_num}")
    # print(f"Pair Filter Number: {pair_filter_num}")
    # print(f"Tuple Filter Number: {tuple_filter_num}")
    # print(f"Odd Filter Number: {oe_filter_num}")
    # print(f"Pos Range Filter Number: {prange_filter_num}")
    # print(f"Pos Relation Filter Number: {prel_filter_num}")

    # 保存到文件
    WriteBaseData.writeJsonData(ENHANCE_NUMBER_FILE, {
        NUMBER: num_enhance,
        SUM_PROB: sum_enhance_num,
        DIFF_PROB: diff_enhance_num,
        PAIR_PROB: pair_enhance_num,
        TUPLE_PROB: tuple_enhance_num,
        ODD_EVEN_RATIO: oe_enhance_num,
        POSITION_RANGE: prange_enhance_num,
        POSITION_RELATION: prel_enhance_num
    })
    
    # print("概率数据已保存到", ENHANCE_NUMBER_FILE)
    # print(f"Sum Filter Number: {sum_enhance_num}")
    # print(f"Diff Filter Number: {diff_enhance_num}")
    # print(f"Pair Filter Number: {pair_enhance_num}")
    # print(f"Tuple Filter Number: {tuple_enhance_num}")
    # print(f"Odd Filter Number: {oe_enhance_num}")
    # print(f"Pos Range Filter Number: {prange_enhance_num}")
    # print(f"Pos Relation Filter Number: {prel_enhance_num}")

    print("All data processed successfully.")

if __name__ == "__main__":
    main()
    #InitAuxiliaryProb.getSingleProbability(PAIR_PROB)





