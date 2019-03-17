package main

import (
	"../dao"
	"fmt"
)

func main() {
	dao.RedisInsert([]string{"拉勾"}, []string{"b"}, "c")
	for k, v := range map[string]string{"a": "1", "b": "2"} {
		fmt.Println(k, v)
	}
}
