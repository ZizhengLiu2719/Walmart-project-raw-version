package models

import (
	"encoding/xml"
)

type WeatherAlerts struct {
	XMLName xml.Name       `xml:"WeatherAlerts`
	Alerts  []WeatherAlert `xml:"WeatherAlert"`
}
