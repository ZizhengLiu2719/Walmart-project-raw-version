package com.transport_service.model;

import com.opencsv.bean.CsvBindByPosition;

/**
 * Represents a single transportation record.
 * Author: Michael
 */
public class TransportRecord {
    @CsvBindByPosition(position = 0)
    private String id;
    @CsvBindByPosition(position = 1)
    private String vehicleType;
    @CsvBindByPosition(position = 2)
    private String origin;
    @CsvBindByPosition(position = 3)
    private String destination;
    @CsvBindByPosition(position = 4)
    private String departureTime;
    @CsvBindByPosition(position = 5)
    private String arrivalTime;
    @CsvBindByPosition(position = 6)
    private String status;
    @CsvBindByPosition(position = 7)
    private String area;

    // Basic validation method as per review feedback
    public boolean hasRequiredFields() {
        return id != null && !id.isBlank() &&
               vehicleType != null && !vehicleType.isBlank() &&
               origin != null && !origin.isBlank() &&
               destination != null && !destination.isBlank() &&
               status != null && !status.isBlank();
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getVehicleType() { return vehicleType; }
    public void setVehicleType(String vehicleType) { this.vehicleType = vehicleType; }
    public String getOrigin() { return origin; }
    public void setOrigin(String origin) { this.origin = origin; }
    public String getArea() { return area; }
    public void setArea(String area) { this.area = area; }
    public String getDestination() { return destination; }
    public void setDestination(String destination) { this.destination = destination; }
    public String getDepartureTime() { return departureTime; }
    public void setDepartureTime(String departureTime) { this.departureTime = departureTime; }
    public String getArrivalTime() { return arrivalTime; }
    public void setArrivalTime(String arrivalTime) { this.arrivalTime = arrivalTime; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
