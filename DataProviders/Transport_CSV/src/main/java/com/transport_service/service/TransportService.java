package com.transport_service.service;

import java.io.InputStreamReader;
import java.io.Reader;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import org.springframework.stereotype.Service;

import com.opencsv.bean.CsvToBeanBuilder;
import com.transport_service.model.TransportRecord;

import jakarta.annotation.PostConstruct;

/**
 * Service to manage transportation records with improved data structures and validation.
 * Author: Michael
 */
@Service
public class TransportService {

    // Using ConcurrentHashMap as suggested for better performance on concurrent read/writes.
    private final ConcurrentMap<String, TransportRecord> records = new ConcurrentHashMap<>();

    @PostConstruct
    public void loadData() {
        try (Reader reader = new InputStreamReader(this.getClass().getResourceAsStream("/data/transport.csv"))) {
            List<TransportRecord> loadedRecords = new CsvToBeanBuilder<TransportRecord>(reader)
                    .withType(TransportRecord.class)
                    .withSkipLines(1) // Skip the header row
                    .withIgnoreLeadingWhiteSpace(true)
                    .build()
                    .parse();
            
            for (TransportRecord record : loadedRecords) {
                if (record.getId() != null && !record.getId().isBlank()) {
                    records.put(record.getId(), record);
                }
            }
            System.out.println("Loaded " + records.size() + " transport records.");
        } catch (Exception e) {
            System.err.println("Error loading transport CSV data: " + e.getMessage());
        }
    }

    public Collection<TransportRecord> getAllRecords() {
        return records.values();
    }

    public Optional<TransportRecord> getRecordById(String id) {
        return Optional.ofNullable(records.get(id));
    }

    public TransportRecord createRecord(TransportRecord record) {
        if (record == null) {
            throw new IllegalArgumentException("Record cannot be null.");
        }
        // If ID is missing, generate one. In a real app, this logic could be more complex.
            // Validate area field 
            if (record.getArea() == null || record.getArea().isBlank()) {
                System.out.println("Warning: Area field is missing for record id=" + record.getId());
            }
        if (record.getId() == null || record.getId().isBlank()) {
            record.setId(UUID.randomUUID().toString());
        }
        // Basic validation as per review feedback
        if (!record.hasRequiredFields()) {
            throw new IllegalArgumentException("Record is missing required fields.");
        }
        records.put(record.getId(), record);
        return record;
    }

    public Optional<TransportRecord> updateRecord(String id, TransportRecord updatedRecord) {
        if (updatedRecord == null) {
            return Optional.empty(); // Or throw exception
        }
        // Basic validation as per review feedback
        if (!updatedRecord.hasRequiredFields()) {
             return Optional.empty(); // Or throw exception
        }

        return Optional.ofNullable(records.computeIfPresent(id, (key, existingRecord) -> {
            updatedRecord.setId(id); // Ensure ID remains consistent
            return updatedRecord;
        }));
    }

    public boolean deleteRecord(String id) {
        // remove() returns the value if key existed, or null otherwise.
        // This provides effective error checking.
        return records.remove(id) != null;
    }
}
