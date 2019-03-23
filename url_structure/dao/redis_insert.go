package dao

import (
	"../config"
	"fmt"
	"github.com/garyburd/redigo/redis"
)

func RedisInsert(platform, city []string, keyword string) {
	c, _ := redis.Dial("tcp", config.RedisHost+":"+config.RedisPort)
	construct := ConstructUrl(platform, city, keyword)
	for k, v := range construct {
		for _, url := range v {
			_, _ = c.Do("sadd", k, url)
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
				result[k[plat]] = make([]string, 0, 5)
			}
			result[k[plat]] = append(result[k[plat]], p[plat](c, keyword))
			fmt.Println(p, c)
		}
	}
	fmt.Println(result)
	return result
}

type F func(city, keyword string) string

func ConstructLagou(city, keyword string) string {
	return "lagou"
}

func ConstructBoss(city, keyword string) string {
	return "boss"
}

func ConstructZhilian(city, keyword string) string {
	return "zhilian"
}

func Construct51(city, keyword string) string {
	return "51"
}
