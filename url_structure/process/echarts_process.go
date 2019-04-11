package process

import (
	"fmt"
	"regexp"
	"strconv"
)

func ExperienceHandle(experience []string) map[string]int {
	result := make(map[string]int)
	for _, element := range experience {
		if element == "" {
			continue
		}
		result[element] += 1
	}
	return result
}

func EducationHandle(education []string) map[string]int {
	result := make(map[string]int)
	for _, element := range education {
		if element == "" {
			continue
		}
		result[element] += 1
	}
	return result
}

func SalaryHandle(salaryDistribution map[string][]string) map[string]map[string]int {
	result := map[string]map[string]int{
		"大专以下": {
			"5k以下":    0,
			"5k-8k":   0,
			"8k-10k":  0,
			"10k-15k": 0,
			"15k-20k": 0,
			"20k-30k": 0,
			"30k-50k": 0,
			"50k以上":   0,
		}, "大专": {
			"5k以下":    0,
			"5k-8k":   0,
			"8k-10k":  0,
			"10k-15k": 0,
			"15k-20k": 0,
			"20k-30k": 0,
			"30k-50k": 0,
			"50k以上":   0,
		}, "本科": {
			"5k以下":    0,
			"5k-8k":   0,
			"8k-10k":  0,
			"10k-15k": 0,
			"15k-20k": 0,
			"20k-30k": 0,
			"30k-50k": 0,
			"50k以上":   0,
		}, "硕士": {
			"5k以下":    0,
			"5k-8k":   0,
			"8k-10k":  0,
			"10k-15k": 0,
			"15k-20k": 0,
			"20k-30k": 0,
			"30k-50k": 0,
			"50k以上":   0,
		}, "博士": {
			"5k以下":    0,
			"5k-8k":   0,
			"8k-10k":  0,
			"10k-15k": 0,
			"15k-20k": 0,
			"20k-30k": 0,
			"30k-50k": 0,
			"50k以上":   0,
		},
	}
	var key string
	re, _ := regexp.Compile(`[\d]+`)
	for i := 0; i < len(salaryDistribution["salary"]); i++ {
		fmt.Println(salaryDistribution["salary"][i])
		temp := re.FindAll([]byte(salaryDistribution["salary"][i]), 2)
		if len(temp) == 2 {
			salaryBegin, _ := strconv.Atoi(string(temp[0]))
			salaryEnd, _ := strconv.Atoi(string(temp[1]))
			avg := (salaryBegin + salaryEnd) / 2
			if avg < 5 {
				key = "5k以下"
			} else if avg < 8 {
				key = "5k-8k"
			} else if avg < 10 {
				key = "8k-10k"
			} else if avg < 15 {
				key = "10k-15k"
			} else if avg < 20 {
				key = "15k-20k"
			} else if avg < 30 {
				key = "20k-30k"
			} else if avg < 50 {
				key = "30k-50k"
			} else {
				key = "50k以上"
			}
			if result[salaryDistribution["education"][i]] != nil {
				result[salaryDistribution["education"][i]][key] += 1
			} else {
				result["大专以下"][key] += 1
			}
		}
	}
	fmt.Println(result)
	return result
}

//func SalaryHandle(salary map[string][]string) map[string]int{
//	result := map[string]int{
//		"5k以下": 0,
//		"5k-8k": 0,
//		"8k-10k": 0,
//		"10k-15k": 0,
//		"15k-20k": 0,
//		"20k-30k": 0,
//		"30k-50k": 0,
//		"50k以上": 0,
//	}
//	var key string
//	re, _ := regexp.Compile(`[\d]+`)
//	for _, element := range salary{
//		if element == ""	{continue}
//		temp := re.FindAll([]byte(element), 2)
//		if temp != nil{
//			salaryBegin, _ := strconv.Atoi(string(temp[0]))
//			salaryEnd, _ := strconv.Atoi(string(temp[1]))
//			avg := (salaryBegin + salaryEnd) / 2
//			if avg < 5{
//				key = "5k以下"
//			}else if avg < 8{
//				key = "5k-8k"
//			}else if avg < 10{
//				key = "8k-10k"
//			}else if avg < 15{
//				key = "10k-15k"
//			}else if avg < 20{
//				key = "15k-20k"
//			}else if avg < 30{
//				key = "20k-30k"
//			}else if avg < 50{
//				key = "30k-50k"
//			}else{
//				key = "50k以上"
//			}
//			result[key] += 1
//		}
//
//	}
//	return result
//}
