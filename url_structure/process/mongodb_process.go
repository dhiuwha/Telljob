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

type FilteredData struct {
	ExperienceRequirement  string `bson:"experience_requirement"`
	EducationalRequirement string `bson:"educational_requirement"`
	Salary                 string `bson:"salary"`
}

type single struct {
	FirstInfo  detail
	SecondInfo detail
}

type total map[string][]Data
type detail []string

func BuildSinglePage(page int, city, platform []string, keyword string) map[string][]Data {
	result := make(total)
	for k, v := range GetSinglePage(page, city, platform, keyword) {
		result[k] = append(result[k], v...)
	}
	return result
}

func BuildSingle(id, platform string) Data {
	return GetOne(bson.ObjectIdHex(id), platform)
}

func BuildTotal(city, platform []string, keyword string) map[string][]string {
	result := make(map[string][]string)
	for _, element := range GetAll(city, platform, keyword) {
		result["salary"] = append(result["salary"], element.Salary)
		result["experience"] = append(result["experience"], element.ExperienceRequirement)
		result["education"] = append(result["education"], element.EducationalRequirement)
	}
	return result
}

func GetSinglePage(page int, city, platform []string, keyword string) map[string][]Data {
	today, _ := time.Parse("2006-01-02", time.Now().AddDate(0, 0, 0).Format("2006-01-02"))
	tomorrow, _ := time.Parse("2006-01-02", time.Now().AddDate(0, 0, 1).Format("2006-01-02"))
	insertTime := bson.M{
		"$gte": today,
		"$lt":  tomorrow,
	}
	result := make(map[string][]Data)
	for _, p := range platform {
		conn, cursor := dao.Connect("tell_job", platformMap[p])
		for _, c := range city {
			var data []Data
			dao.FindSinglePage(cursor, page*5, bson.M{"keyword": keyword, "city": c, "insert_time": insertTime}, &data)
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

func GetAll(city, platform []string, keyword string) []FilteredData {
	today, _ := time.Parse("2006-01-02", time.Now().AddDate(0, 0, 0).Format("2006-01-02"))
	tomorrow, _ := time.Parse("2006-01-02", time.Now().AddDate(0, 0, 1).Format("2006-01-02"))
	insertTime := bson.M{
		"$gte": today,
		"$lt":  tomorrow,
	}
	result := make([]FilteredData, 1)
	for _, p := range platform {
		conn, cursor := dao.Connect("tell_job", platformMap[p])
		for _, c := range city {
			aggregation := []bson.M{
				{"$match": bson.M{"keyword": keyword, "city": c, "insert_time": insertTime}},
				{"$project": bson.M{"_id": 0, "salary": 1, "experience_requirement": 1, "educational_requirement": 1}},
			}
			var data []FilteredData
			dao.FindAll(cursor, aggregation, &data)
			result = append(result, data...)
		}
		conn.Close()
	}
	return result
}

func Filter(platform, city, keyword string) bool {
	//fmt.Println(platform, city, keyword)
	var data Data
	conn, cursor := dao.Connect("tell_job", platform)
	defer conn.Close()
	dao.FindOne(cursor, bson.M{"city": city, "keyword": keyword}, &data)
	return data.InsertTime.Format("2006-01-02") == time.Now().Format("2006-01-02")
}
