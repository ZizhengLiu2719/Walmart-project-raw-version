package handlers

import (
	"embed"
	"encoding/xml"
	"fmt"
	"io"
	"net/http"
	"strconv"

	"walmart-datafusion/DataProviders/National_Weather_Service/internal/models"
)

type Http_Handler struct {
	Weather_Alerts *[]models.WeatherAlert
}

//go:embed openapi.yaml
var openapiFS embed.FS

func NewHttpHandler(alerts *[]models.WeatherAlert) *Http_Handler {
	return &Http_Handler{Weather_Alerts: alerts}
}

func (http_handler *Http_Handler) SetupRoutes() {
	http.HandleFunc("/weather-alert", http_handler.enableCors(http_handler.weatherAlertsHandler))
	http.HandleFunc("/api-docs.yaml", http_handler.enableCors(http_handler.serveOpenAPISpec))
}

//*********************************************************************************************
//* CRUD HANDLER
//*********************************************************************************************
func (http_handler *Http_Handler) serveOpenAPISpec(w http.ResponseWriter, r *http.Request) {
	data, err := openapiFS.ReadFile("openapi.yaml")
	if err != nil {
		http.Error(w, "OpenAPI not found", http.StatusInternalServerError)
		fmt.Println(err)
		return
	}

	w.Write(data)
}


func (http_handler *Http_Handler) weatherAlertsHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:

		if idStr := r.URL.Query().Get("id"); idStr == "" {
			// READ (all)
			fmt.Println("No ID")
			send(w, *http_handler.Weather_Alerts)
		} else {
			idInt, err := strconv.Atoi(idStr)
			if err != nil {
				http.Error(w, "Error while parsing id. Please send only an integer", http.StatusBadRequest)
				return
			}

			if idInt >= 0 && idInt < len(*http_handler.Weather_Alerts) {
				weatherAlert := (*http_handler.Weather_Alerts)[idInt]
				send(w, weatherAlert)
			} else {
				http.Error(w, "id is out of bounds", http.StatusBadRequest)
			}
		}

	case http.MethodPost:
		// CREATE
		var newAlert models.WeatherAlert
		if err := xml.NewDecoder(r.Body).Decode(&newAlert); err != nil {
			http.Error(w, "Invalid XML payload", http.StatusBadRequest)
			return
		}
		*http_handler.Weather_Alerts = append(*http_handler.Weather_Alerts, newAlert)
		w.WriteHeader(http.StatusCreated)
		send(w, newAlert)

	case http.MethodPut:
		// UPDATE (expects ?id= index in slice for simplicity)
		idStr := r.URL.Query().Get("id")
		if idStr == "" {
			http.Error(w, "Missing id parameter", http.StatusBadRequest)
			return
		}
		id, err := strconv.Atoi(idStr)
		if err != nil || id < 0 || id >= len(*http_handler.Weather_Alerts) {
			http.Error(w, "Invalid id parameter", http.StatusBadRequest)
			return
		}

		var updatedAlert models.WeatherAlert
		body, _ := io.ReadAll(r.Body)
		if err := xml.Unmarshal(body, &updatedAlert); err != nil {
			http.Error(w, "Invalid XML payload", http.StatusBadRequest)
			return
		}

		(*http_handler.Weather_Alerts)[id] = updatedAlert
		send(w, updatedAlert)

	case http.MethodDelete:
		// DELETE (expects ?id= index in slice for simplicity)
		idStr := r.URL.Query().Get("id")
		if idStr == "" {
			http.Error(w, "Missing id parameter", http.StatusBadRequest)
			return
		}
		id, err := strconv.Atoi(idStr)
		if err != nil || id < 0 || id >= len(*http_handler.Weather_Alerts) {
			http.Error(w, "Invalid id parameter", http.StatusBadRequest)
			return
		}

		alerts := *http_handler.Weather_Alerts
		*http_handler.Weather_Alerts = append(alerts[:id], alerts[id+1:]...)
		w.WriteHeader(http.StatusNoContent)

	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

//*********************************************************************************************
//* HELPERS
//*********************************************************************************************

func (http_handler *Http_Handler) enableCors(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == http.MethodOptions {
			w.WriteHeader(http.StatusOK)
			return
		}
		next(w, r)
	}
}

func send[T any](w http.ResponseWriter, data T) {
	w.Header().Set("Content-Type", "application/xml")
	if err := xml.NewEncoder(w).Encode(data); err != nil {
		http.Error(w, "Failed to encode response", http.StatusInternalServerError)
	}
}
