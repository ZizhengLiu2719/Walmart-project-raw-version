package com.Healthcare_Service.patient.service;

import com.Healthcare_Service.patient.model.PatientRecord;
import com.Healthcare_Service.patient.faults.NotFoundException;

import jakarta.jws.WebMethod;
import jakarta.jws.WebService;
import jakarta.jws.WebParam;

@WebService(targetNamespace = "http://Healthcare_Service.com/patient", name = "PatientRecordsService")
public interface PatientRecordsService {
  @WebMethod
  String createPatient(@WebParam(name = "patient") PatientRecord patient);

  @WebMethod
  PatientRecord getPatient(@WebParam(name = "id") String id) throws NotFoundException;

  @WebMethod
  boolean updatePatient(@WebParam(name = "patient") PatientRecord patient) throws NotFoundException;

  @WebMethod
  boolean deletePatient(@WebParam(name = "id") String id) throws NotFoundException;
}
