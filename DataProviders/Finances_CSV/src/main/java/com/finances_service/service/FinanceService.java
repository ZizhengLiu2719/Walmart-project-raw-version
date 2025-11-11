package com.finances_service.service;

import java.io.InputStreamReader;
import java.io.Reader;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import org.springframework.stereotype.Service;

import com.finances_service.model.FinancialRecord;
import com.opencsv.bean.CsvToBeanBuilder;

import jakarta.annotation.PostConstruct;

/**
 * Service to manage financial records with improved data structures and validation.
 * Author: Michael
 */
@Service
public class FinanceService {

    // Using ConcurrentHashMap as suggested for better performance on concurrent read/writes.
    private final ConcurrentMap<String, FinancialRecord> records = new ConcurrentHashMap<>();

    @PostConstruct
    public void loadData() {
        try (Reader reader = new InputStreamReader(this.getClass().getResourceAsStream("/data/finances.csv"))) {
            List<FinancialRecord> loadedRecords = new CsvToBeanBuilder<FinancialRecord>(reader)
                    .withType(FinancialRecord.class)
                    .withSkipLines(1) // Skip header row
                    .build()
                    .parse();
            
            for (FinancialRecord record : loadedRecords) {
                if (record.getId() != null && !record.getId().isBlank()) {
                    records.put(record.getId(), record);
                }
            }
            System.out.println("Loaded " + records.size() + " financial records.");
        } catch (Exception e) {
            System.err.println("Error loading finances CSV data: " + e.getMessage());
        }
    }

    public Collection<FinancialRecord> getAllRecords() {
        return records.values();
    }

    public Optional<FinancialRecord> getRecordById(String id) {
        return Optional.ofNullable(records.get(id));
    }

    public FinancialRecord createRecord(FinancialRecord record) {
        if (record == null) {
            throw new IllegalArgumentException("Record cannot be null.");
        }
        if (record.getId() == null || record.getId().isBlank()) {
            record.setId(UUID.randomUUID().toString());
        }
        if (!record.hasRequiredFields()) {
            throw new IllegalArgumentException("Record is missing required fields.");
        }
        records.put(record.getId(), record);
        return record;
    }

    public Optional<FinancialRecord> updateRecord(String id, FinancialRecord updatedRecord) {
        if (updatedRecord == null || !updatedRecord.hasRequiredFields()) {
            return Optional.empty(); // Or throw exception for invalid data
        }

        return Optional.ofNullable(records.computeIfPresent(id, (key, existingRecord) -> {
            updatedRecord.setId(id); // Ensure ID remains consistent
            return updatedRecord;
        }));
    }

    public boolean deleteRecord(String id) {
        // remove() returns the value if key existed, or null otherwise.
        return records.remove(id) != null;
    }
}
