package com.Healthcare_Service.patient.faults;

import jakarta.xml.ws.WebFault;

@WebFault(name = "NotFoundFault")
public class NotFoundException extends Exception {
  private static final long serialversionUID = 1L;

  public NotFoundException(String message) {
    super(message);
  }

  public NotFoundException(String message, Throwable cause) {
    super(message, cause);
  }

}
