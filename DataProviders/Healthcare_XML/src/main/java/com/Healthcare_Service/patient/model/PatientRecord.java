package com.Healthcare_Service.patient.model;

import jakarta.xml.bind.annotation.XmlRootElement;
import jakarta.xml.bind.annotation.XmlAccessorType;
import jakarta.xml.bind.annotation.XmlAccessType;
import java.io.Serializable;

@XmlRootElement(name = "PatientRecord")
@XmlAccessorType(XmlAccessType.FIELD)
public class PatientRecord implements Serializable {
  private static final long serialVersionUID = 1L;

  public String id;
  public String name;
  public String dateOfBirth; // ISO yyyy-MM-dd recommended
  public String notes;
  public int age;
  public String condition;

  public PatientRecord() {
  }

  public PatientRecord(String id, String name, String dateOfBirth, String notes, int age, String condition) {
    this.id = id;
    this.name = name;
    this.dateOfBirth = dateOfBirth;
    this.notes = notes;
    this.age = age;
    this.condition = condition;
  }

  @Override
  public String toString() {
    return "PatientRecord{id=" + this.id + " , name=" + this.name + "}";
  }
}
