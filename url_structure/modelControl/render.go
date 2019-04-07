package modelControl

import (
	"../process"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/globalsign/mgo/bson"
	"html/template"
	"net/http"
	"strings"
)

type PositionInfo struct {
	Source    string `form:"source" json:"source"`
	Address   string `form:"address" json:"address"`
	Keyword   string `form:"keyword" json:"keyword"`
	Timestamp int    `form:"timestamp" json:"timestamp"`
}

var city = make([]string, 1)
var platform = make([]string, 1)
var keyword string

func BuildUrl(id bson.ObjectId, platform string) string {
	fmt.Println(id.Hex())
	return "http://localhost:5000/position?id=" + id.Hex() + "&platform=" + platform
}

func startPage(c *gin.Context) {
	var person PositionInfo
	if c.ShouldBindJSON(&person) != nil {
		city = strings.Split(person.Address, ",")
		platform = strings.Split(person.Source, ",")
		keyword = person.Keyword
		//dao.RedisInsert(platform, city, keyword)
	}
	c.JSON(200, gin.H{
		"status": "Success",
	})
}

func jobPage(c *gin.Context) {
	c.HTML(http.StatusOK, "spider.tmpl", gin.H{
		"city":      city,
		"platform":  platform,
		"info":      process.BuildTotal(city, platform, keyword),
		"build_url": BuildUrl,
	})
}

func queryPosition(c *gin.Context) {
	id := c.Query("id")
	platform := c.Query("platform")
	fmt.Println(id)
	c.HTML(http.StatusOK, "detail.tmpl", gin.H{
		"detail": process.BuildSingle(id, platform),
	})
}

func Cors() gin.HandlerFunc {
	return func(c *gin.Context) {
		method := c.Request.Method               //请求方法
		origin := c.Request.Header.Get("Origin") //请求头部
		var headerKeys []string                  // 声明请求头keys
		for k := range c.Request.Header {
			headerKeys = append(headerKeys, k)
		}
		headerStr := strings.Join(headerKeys, ", ")
		if headerStr != "" {
			headerStr = fmt.Sprintf("access-control-allow-origin, access-control-allow-headers, %s", headerStr)
		} else {
			headerStr = "access-control-allow-origin, access-control-allow-headers"
		}
		if origin != "" {
			c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
			c.Header("Access-Control-Allow-Origin", "*")                                       // 这是允许访问所有域
			c.Header("Access-Control-Allow-Methods", "POST, GET, OPTIONS, PUT, DELETE,UPDATE") //服务器支持的所有跨域请求的方法,为了避免浏览次请求的多次'预检'请求
			//  header的类型
			c.Header("Access-Control-Allow-Headers", "Authorization, Content-Length, X-CSRF-Token, Token,session,X_Requested_With,Accept, Origin, Host, Connection, Accept-Encoding, Accept-Language,DNT, X-CustomHeader, Keep-Alive, User-Agent, X-Requested-With, If-Modified-Since, Cache-Control, Content-Type, Pragma")
			//              允许跨域设置                                                                                                      可以返回其他子段
			c.Header("Access-Control-Expose-Headers", "Content-Length, Access-Control-Allow-Origin, Access-Control-Allow-Headers,Cache-Control,Content-Language,Content-Type,Expires,Last-Modified,Pragma,FooBar") // 跨域关键设置 让浏览器可以解析
			c.Header("Access-Control-Max-Age", "172800")                                                                                                                                                           // 缓存请求信息 单位为秒
			c.Header("Access-Control-Allow-Credentials", "false")                                                                                                                                                  //  跨域请求是否需要带cookie信息 默认设置为true
			c.Set("content-type", "application/json")                                                                                                                                                              // 设置返回格式是json
		}

		//放行所有OPTIONS方法
		if method == "OPTIONS" {
			c.JSON(http.StatusOK, "Options Request!")
		}
		// 处理请求
		c.Next() //  处理请求
	}
}

func Router() {
	router := gin.Default()
	router.Use(Cors())
	router.SetFuncMap(template.FuncMap{
		"buildUrl": BuildUrl,
	})
	router.LoadHTMLFiles("ugly_face/basic.html", "ugly_face/detail.html")

	router.POST("/post", startPage)
	router.GET("/upload", jobPage)
	router.GET("/position", queryPosition)
	_ = router.Run("0.0.0.0:5000")
}
