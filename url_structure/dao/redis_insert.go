package dao

import (
	"../config"
	"fmt"
	"github.com/garyburd/redigo/redis"
	"strconv"
)

func RedisInsert(platform, city []string, keyword string) {
	c, _ := redis.Dial("tcp", config.RedisHost+":"+config.RedisPort, redis.DialDatabase(1))
	construct := ConstructUrl(platform, city, keyword)
	for k, v := range construct {
		for _, url := range v {
			_, _ = c.Do("lpush", k, url)
		}
	}
}

func ConstructUrl(platform, city []string, keyword string) map[string][]string {
	p := map[string]F{
		"拉勾": ConstructLagou,
		"直聘": ConstructBoss,
		"智联": ConstructZhilian,
		"51": Construct51,
	}
	k := map[string]string{
		"拉勾": "lagou:start_urls",
		"直聘": "boss:start_urls",
		"智联": "zhilian:start_urls",
		"51": "51job:start_urls",
	}
	result := make(map[string][]string)
	for _, plat := range platform {
		for _, c := range city {
			_, judge := result[k[plat]]
			if judge {
				result[k[plat]] = make([]string, 1)
			}
			result[k[plat]] = append(result[k[plat]], p[plat](c, keyword)...)
			fmt.Println(p, c)
		}
	}
	fmt.Println(result)
	return result
}

type F func(city, keyword string) []string

func ConstructLagou(city, keyword string) []string {
	result := make([]string, 1)
	for i := 0; i < 5; i++ {
		print()
		result = append(result, "https://www.lagou.com/jobs/list_"+keyword+"?labelWords=&fromSearch=true&suginput="+
			"{\"city\":\""+city+"\", \"keyword\":\""+keyword+"\",\"page\": \""+strconv.Itoa(i+1)+"\"}")
	}

	return result
}

func ConstructBoss(city, keyword string) []string {
	result := make([]string, 1)
	cityMap := map[string]string{
		"北京": "101010100",
		"上海": "101020100",
		"广州": "101280100",
		"深圳": "101280600",
	}
	for i := 0; i < 5; i++ {
		print()
		result = append(result, "https://www.zhipin.com/c"+cityMap[city]+"/?query="+keyword+"&page="+strconv.Itoa(i+1)+"&ka=page-"+strconv.Itoa(i+1)+
			"{\"city\":\""+city+"\", \"keyword\":\""+keyword+"\"}")
	}

	return result
}

func ConstructZhilian(city, keyword string) []string {
	result := make([]string, 1)
	cityMap := map[string]string{
		"北京": "530",
		"上海": "538",
		"广州": "763",
		"深圳": "765",
	}
	for i := 0; i < 5; i++ {
		print()
		result = append(result, "https://fe-api.zhaopin.com/c/i/sou?start="+strconv.Itoa(i*90)+"&pageSize=90&cityId="+cityMap[city]+"&kw="+keyword+"&kt=3"+
			"{\"city\":\""+city+"\", \"keyword\":\""+keyword+"\"}")
	}

	return result
}

func Construct51(city, keyword string) []string {
	result := make([]string, 1)
	cityMap := map[string]string{
		"北京": "010000,000000,0000,00",
		"上海": "020000,000000,0000,00",
		"广州": "030200,000000,0000,00",
		"深圳": "040000,000000,0000,00",
	}
	for i := 0; i < 5; i++ {
		print()
		result = append(result, "https://search.51job.com/list/"+cityMap[city]+",9,99,"+keyword+",2,"+strconv.Itoa(i+1)+".html"+
			"{\"city\":\""+city+"\", \"keyword\":\""+keyword+"\"}")
	}

	return result
}
