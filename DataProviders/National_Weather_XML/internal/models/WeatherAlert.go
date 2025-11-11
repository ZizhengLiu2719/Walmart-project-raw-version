package models

type WeatherAlert struct {
	Event     string `xml:"Event"`
	Effective string `xml:"Effective"`
	Expires   string `xml:"Expires"`
	Area      string `xml:"Area"`
	Summary   string `xml:"Summary"`
}
