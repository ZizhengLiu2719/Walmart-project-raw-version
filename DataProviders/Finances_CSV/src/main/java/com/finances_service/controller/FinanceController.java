package com.finances_service.controller;

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

import com.finances_service.model.FinancialRecord;
import com.finances_service.service.FinanceService;
import com.finances_service.util.CsvConverter;

/**
 * REST Controller for Financial Records, reworked to return CSV.
 * Author: Michael
 */
@RestController
@RequestMapping("/finances")
public class FinanceController {

    private final FinanceService financeService;
    private final CsvConverter csvConverter;

    public FinanceController(FinanceService financeService, CsvConverter csvConverter) {
        this.financeService = financeService;
        this.csvConverter = csvConverter;
    }

    @GetMapping
    public ResponseEntity<String> getAllRecords() {
        String csv = csvConverter.convertToCsv(financeService.getAllRecords());
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.TEXT_PLAIN);
        headers.setContentDispositionFormData("attachment", "finances.csv");
        return new ResponseEntity<>(csv, headers, HttpStatus.OK);
    }

    @GetMapping("/{id}")
    public ResponseEntity<String> getRecordById(@PathVariable String id) {
        return financeService.getRecordById(id)
                .map(record -> {
                    String csv = csvConverter.convertToCsv(Collections.singletonList(record));
                    HttpHeaders headers = new HttpHeaders();
                    headers.setContentType(MediaType.TEXT_PLAIN);
                    headers.setContentDispositionFormData("attachment", "finance_" + id + ".csv");
                    return new ResponseEntity<>(csv, headers, HttpStatus.OK);
                })
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping(consumes = MediaType.TEXT_PLAIN_VALUE)
    public ResponseEntity<String> createRecord(@RequestBody String csvData) {
        try {
            List<FinancialRecord> records = csvConverter.convertFromCsv(csvData);
            if (records.isEmpty()) {
                return ResponseEntity.badRequest().build();
            }
            // Assume the POST request sends one record to create
            FinancialRecord recordToCreate = records.get(0);

            FinancialRecord createdRecord = financeService.createRecord(recordToCreate);
            
            // Convert the single created record back to CSV for the response
            String csvResponse = csvConverter.convertToCsv(Collections.singletonList(createdRecord));
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.TEXT_PLAIN);
            
            return new ResponseEntity<>(csvResponse, headers, HttpStatus.CREATED);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    @PutMapping(value = "/{id}", consumes = MediaType.TEXT_PLAIN_VALUE)
    public ResponseEntity<String> updateRecord(@PathVariable String id, @RequestBody String csvData) {
        try {
            List<FinancialRecord> records = csvConverter.convertFromCsv(csvData);
            if (records.isEmpty()) {
                return ResponseEntity.badRequest().build();
            }
            FinancialRecord recordToUpdate = records.get(0);

            return financeService.updateRecord(id, recordToUpdate)
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
        if (financeService.deleteRecord(id)) {
            return ResponseEntity.noContent().build();
        }
        return ResponseEntity.notFound().build();
    }
}
