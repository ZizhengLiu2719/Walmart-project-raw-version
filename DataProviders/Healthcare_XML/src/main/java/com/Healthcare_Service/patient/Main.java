package com.Healthcare_Service.patient;

import com.Healthcare_Service.patient.service.PatientRecordsServiceImpl;
import jakarta.xml.ws.Endpoint;

public class Main {
  public static void main(String[] args) {
    int port = 8082;
    String base = "http://localhost:" + port + "/patient-records";
    PatientRecordsServiceImpl impl = new PatientRecordsServiceImpl();

    Endpoint endpoint = Endpoint.publish(base, impl);

    System.out.println("SOAP endpoint started at: " + base);
    System.out.println("WSDL available at " + base + "?wsdl");
    System.out.println("Press Ctrl+C to stop.");
  }
}
