package main

import (
	"../dao"
)

func main() {
	dao.RedisInsert([]string{"拉勾"}, []string{"广州"}, "机器学习")
	//for k, v := range map[string]string{"a": "1", "b": "2"} {
	//	fmt.Println(k, v)
	//}
}
