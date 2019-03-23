package process

import (
	"../dao"
	"github.com/globalsign/mgo/bson"
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
	WorkingPlace           string `bson:"working_place"`
	ExperienceRequirement  string `bson:"experience_requirement"`
	EducationalRequirement string `bson:"educational_requirement"`
	Salary                 string `bson:"salary"`
	CreateTime             string `bson:"create_time"`
}

type total []single
type single map[string]detail
type detail []string

func Build(city, platform []string, keyword string) []single {
	var result total
	for _, element := range GetAll(city, platform, keyword) {
		firstInfo := detail{element.PositionName, element.CompanyName, element.Salary}
		secondInfo := detail{element.WorkingPlace, element.ExperienceRequirement, element.EducationalRequirement}
		result = append(result, single{"first_info": firstInfo, "second_info": secondInfo})
	}
	return result
}

func GetAll(city, platform []string, keyword string) []Data {

	var result []Data
	for _, p := range platform {
		conn, cursor := dao.Connect("tell_job", platformMap[p])
		for _, c := range city {
			var data []Data
			dao.FindAll(cursor, bson.M{"keyword": keyword, "city": c}, &data)
			result = append(result, data...)
		}
		conn.Close()
	}
	return result
}

func GetOne(id bson.ObjectId, platform string) Data {
	var data Data
	conn, cursor := dao.Connect("tell_job", platform)
	defer conn.Close()
	dao.FindAll(cursor, bson.M{"_id": id}, &data)
	//bson.ObjectIdHex("5c8378161e95dc0f04c1a4c2")
	return data
}
