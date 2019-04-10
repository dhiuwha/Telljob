package main

import (
	"../process"
)

func main() {
	process.RedisInsert([]string{"拉勾", "智联", "直聘", "51"}, []string{"广州", "深圳", "上海", "北京"}, "java")
	//for k, v := range map[string]string{"a": "1", "b": "2"} {
	//	fmt.Println(k, v)
	//}
}
