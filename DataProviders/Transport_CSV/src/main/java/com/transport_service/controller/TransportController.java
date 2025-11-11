package com.transport_service.controller;

import java.util.Collections;
import java.util.List;

import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.transport_service.model.TransportRecord;
import com.transport_service.service.TransportService;
import com.transport_service.util.CsvConverter;

/**
 * REST Controller for Transport Records, reworked to return CSV.
 * Author: Michael
 */
@RestController
@RequestMapping("/transport")
public class TransportController {
    // Example: Add endpoint to filter by area
    @GetMapping("/area/{area}")
    public ResponseEntity<List<TransportRecord>> getRecordsByArea(@PathVariable String area) {
        List<TransportRecord> filtered = transportService.getAllRecords().stream()
            .filter(r -> r.getArea() != null && r.getArea().equalsIgnoreCase(area))
            .toList();
        return ResponseEntity.ok(filtered);
    }

    private final TransportService transportService;
    private final CsvConverter csvConverter;

    public TransportController(TransportService transportService, CsvConverter csvConverter) {
        this.transportService = transportService;
        this.csvConverter = csvConverter;
    }

    @GetMapping
    public ResponseEntity<String> getAllRecords() {
        String csv = csvConverter.convertToCsv(transportService.getAllRecords());
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.TEXT_PLAIN); // TEXT_CSV is not a standard media type, TEXT_PLAIN is safer
        headers.setContentDispositionFormData("attachment", "transport.csv");
        return new ResponseEntity<>(csv, headers, HttpStatus.OK);
    }

    @GetMapping("/{id}")
    public ResponseEntity<String> getRecordById(@PathVariable String id) {
        return transportService.getRecordById(id)
                .map(record -> {
                    String csv = csvConverter.convertToCsv(Collections.singletonList(record));
                    HttpHeaders headers = new HttpHeaders();
                    headers.setContentType(MediaType.TEXT_PLAIN);
                    headers.setContentDispositionFormData("attachment", "transport_" + id + ".csv");
                    return new ResponseEntity<>(csv, headers, HttpStatus.OK);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping(consumes = MediaType.TEXT_PLAIN_VALUE)
    public ResponseEntity<String> createRecord(@RequestBody String csvData) {
        try {
            List<TransportRecord> records = csvConverter.convertFromCsv(csvData);
            if (records.isEmpty()) {
                return ResponseEntity.badRequest().build();
            }
            // Assume the POST request sends one record to create
            TransportRecord recordToCreate = records.get(0);

            TransportRecord createdRecord = transportService.createRecord(recordToCreate);

            // Convert the single created record back to CSV for the response
            String csvResponse = csvConverter.convertToCsv(Collections.singletonList(createdRecord));
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.TEXT_PLAIN);

            return new ResponseEntity<>(csvResponse, headers, HttpStatus.CREATED);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (RuntimeException e) {
            // This will catch parsing errors from CsvConverter
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping(value = "/{id}", consumes = MediaType.TEXT_PLAIN_VALUE)
    public ResponseEntity<String> updateRecord(@PathVariable String id, @RequestBody String csvData) {
        try {
            List<TransportRecord> records = csvConverter.convertFromCsv(csvData);
            if (records.isEmpty()) {
                return ResponseEntity.badRequest().build();
            }
            TransportRecord recordToUpdate = records.get(0);

            return transportService.updateRecord(id, recordToUpdate)
                    .map(updatedRecord -> {
                        String csvResponse = csvConverter.convertToCsv(Collections.singletonList(updatedRecord));
                        HttpHeaders headers = new HttpHeaders();
                        headers.setContentType(MediaType.TEXT_PLAIN);
                        return new ResponseEntity<>(csvResponse, headers, HttpStatus.OK);
                    })
                    .orElse(ResponseEntity.badRequest().build());
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRecord(@PathVariable String id) {
        if (transportService.deleteRecord(id)) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
