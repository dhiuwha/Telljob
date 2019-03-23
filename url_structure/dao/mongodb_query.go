package dao

import (
	"../config"
	"github.com/globalsign/mgo"
	"log"
)

var globalS *mgo.Session

func init() {
	s, err := mgo.Dial(config.MongoDBHost + ":" + config.MongoDBPort)
	if err != nil {
		log.Fatalf("Create Session: %s\n", err)
	}
	globalS = s
}

func Connect(db, collection string) (*mgo.Session, *mgo.Collection) {
	ms := globalS.Copy()
	ms.SetMode(mgo.Monotonic, true)
	c := ms.DB(db).C(collection)

	return ms, c
}

func FindOne(c *mgo.Collection, query, result interface{}) {
	_ = c.Find(query).One(result)
}

func FindAll(c *mgo.Collection, query, result interface{}) {
	_ = c.Find(query).All(result)
}
