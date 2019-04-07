package process

import (
	"../dao"
	"fmt"
	"github.com/globalsign/mgo/bson"
	"time"
)

var platformMap = map[string]string{
	"拉勾": "lagou",
	"智联": "zhilian",
	"直聘": "boss",
	"51": "51job",
}

type Data struct {
	Id           bson.ObjectId `bson:"_id"`
	PositionName string        `bson:"position_name"`
	//PositionUrl            string `bson:"position_url"`
	CompanyName string `bson:"company_name"`
	//CompanyUrl             string `bson:"company_url"`
	WorkingPlace           string    `bson:"working_place"`
	ExperienceRequirement  string    `bson:"experience_requirement"`
	EducationalRequirement string    `bson:"educational_requirement"`
	Salary                 string    `bson:"salary"`
	CreateTime             string    `bson:"publish_time"`
	PositionDetailInfo     []string  `bson:"position_detail_info"`
	InsertTime             time.Time `bson:"insert_time"`
}

type single struct {
	FirstInfo  detail
	SecondInfo detail
}

type total map[string][]Data
type detail []string

func BuildTotal(city, platform []string, keyword string) map[string][]Data {
	result := make(total)
	for k, v := range GetAll(city, platform, keyword) {
		result[k] = append(result[k], v...)
	}
	return result
}

func BuildSingle(id, platform string) Data {
	return GetOne(bson.ObjectIdHex(id), platform)
}

func GetAll(city, platform []string, keyword string) map[string][]Data {

	result := make(map[string][]Data)
	for _, p := range platform {
		conn, cursor := dao.Connect("tell_job", platformMap[p])
		for _, c := range city {
			var data []Data
			dao.FindAll(cursor, bson.M{"keyword": keyword, "city": c}, &data)
			result[platformMap[p]] = append(result[platformMap[p]], data...)
		}
		conn.Close()
	}
	return result
}

func GetOne(id bson.ObjectId, platform string) Data {
	var data Data
	conn, cursor := dao.Connect("tell_job", platform)
	defer conn.Close()
	dao.FindOne(cursor, bson.M{"_id": id}, &data)
	fmt.Println(data)
	return data
}

func Filter(platform, city, keyword string) bool {
	fmt.Println(platform, city, keyword)
	var data Data
	conn, cursor := dao.Connect("tell_job", platform)
	defer conn.Close()
	dao.FindOne(cursor, bson.M{"city": city, "keyword": keyword}, &data)
	return data.InsertTime.Format("2006-01-02") == time.Now().Format("2006-01-02")
}
