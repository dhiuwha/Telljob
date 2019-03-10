package main

import (
	"github.com/gin-gonic/gin"
	"log"
)

type PositionInfo struct {
	Source    string `form:"source"`
	Keyword   string `form:"keyword"`
	Timestamp int    `form:"timestamp"`
}

func startPage(c *gin.Context) {
	var person PositionInfo
	// 将 url 查询参数和person绑定在一起
	if c.ShouldBind(&person) == nil {
		log.Println("====== Only Bind By Query String ======")
		log.Println(person.Source)
		log.Println(person.Keyword)
		log.Println(person.Timestamp)
	}
	c.String(200, "Success")
}

func Route() {
	// 初始化引擎
	router := gin.Default()
	// 注册一个路由和处理函数
	router.Any("/post", startPage)
	_ = router.Run("0.0.0.0:8080")
}
