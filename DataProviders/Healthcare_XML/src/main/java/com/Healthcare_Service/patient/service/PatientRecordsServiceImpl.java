package com.Healthcare_Service.patient.service;

import jakarta.jws.WebService;
import com.Healthcare_Service.patient.model.PatientRecord;
import com.Healthcare_Service.patient.faults.NotFoundException;

import java.util.concurrent.ConcurrentHashMap;
import java.util.UUID;

@WebService(endpointInterface = "com.Healthcare_Service.patient.service.PatientRecordsService", serviceName = "PatientRecordsService", portName = "PatientRecordsPort", targetNamespace = "http://Healthcare_Service.com/patient")
public class PatientRecordsServiceImpl implements PatientRecordsService {
  private final ConcurrentHashMap<String, PatientRecord> store = new ConcurrentHashMap<>();

  @Override
  public String createPatient(PatientRecord patient) {
    String id = (patient == null || patient.id == null || patient.id.isBlank())
        ? UUID.randomUUID().toString()
        : patient.id;

    patient.id = id;
    store.put(id, patient);
    return id;
  }

  @Override
  public PatientRecord getPatient(String id) throws NotFoundException {
    PatientRecord p = store.get(id);
    if (p == null)
      throw new NotFoundException("Patient not found with id: " + id);
    return p;
  }

  @Override
  public boolean updatePatient(PatientRecord patient) throws NotFoundException {
    if (patient == null || patient.id == null)
      throw new NotFoundException("Missing patient id for update");
    if (!store.containsKey(patient.id))
      throw new NotFoundException("No patient with id: " + patient.id);
    store.put(patient.id, patient);
    return true;
  }

  @Override
  public boolean deletePatient(String id) throws NotFoundException {
    PatientRecord removed = store.remove(id);
    if (removed == null)
      throw new NotFoundException("No patient with id: " + id);
    return true;
  }

}
