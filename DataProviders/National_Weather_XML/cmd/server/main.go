package main

import (
	"encoding/xml"
	"fmt"
	"log"
	"net/http"
	"os"

	"walmart-datafusion/DataProviders/National_Weather_Service/internal/handlers"
	"walmart-datafusion/DataProviders/National_Weather_Service/internal/models"
)

func main() {

	alerts, err := parseWeatherAlertsDatafile()
	if err != nil {
		panic(err)
	}

	fmt.Println(len(alerts))

	http_handler := handlers.NewHttpHandler(&alerts)
	http_handler.SetupRoutes()

	fmt.Println("Starting server at :8081")
	log.Fatal(http.ListenAndServe(":8081", nil))
}

func parseWeatherAlertsDatafile() ([]models.WeatherAlert, error) {
	var container models.WeatherAlerts

	file, err := os.Open("./../../internal/datafiles/WeatherAlerts.xml")
	if err != nil {
		return nil, err
	}
	defer file.Close()

	decoder := xml.NewDecoder(file)
	if err := decoder.Decode(&container); err != nil {
		return nil, err
	}

	return container.Alerts, nil
}
