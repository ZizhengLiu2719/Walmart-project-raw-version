package com.transport_service.util;

import java.io.Reader;
import java.io.StringReader;
import java.io.StringWriter;
import java.util.Collection;
import java.util.Collections;
import java.util.List;

import org.springframework.stereotype.Component;

import com.opencsv.bean.CsvToBeanBuilder;
import com.opencsv.bean.StatefulBeanToCsv;
import com.opencsv.bean.StatefulBeanToCsvBuilder;
import com.opencsv.exceptions.CsvDataTypeMismatchException;
import com.opencsv.exceptions.CsvRequiredFieldEmptyException;
import com.transport_service.model.TransportRecord;

/**
 * Utility to convert TransportRecord objects to and from CSV format.
 * Author: Michael
 */
@Component
public class CsvConverter {

    public String convertToCsv(Collection<TransportRecord> records) {
        if (records == null || records.isEmpty()) {
            return "";
        }

        try (StringWriter writer = new StringWriter()) {
            StatefulBeanToCsv<TransportRecord> beanToCsv = new StatefulBeanToCsvBuilder<TransportRecord>(writer).build();
            beanToCsv.write(records.stream());
            return writer.toString();
        } catch (CsvDataTypeMismatchException | CsvRequiredFieldEmptyException e) {
            // In a real app, log this exception properly
            System.err.println("Error converting to CSV: " + e.getMessage());
            throw new RuntimeException("Failed to convert records to CSV", e);
        } catch (Exception e) {
            System.err.println("An unexpected error occurred during CSV conversion: " + e.getMessage());
            throw new RuntimeException("An unexpected error occurred during CSV conversion", e);
        }
    }

    public List<TransportRecord> convertFromCsv(String csv) {
        if (csv == null || csv.isBlank()) {
            return Collections.emptyList();
        }

        try (Reader reader = new StringReader(csv)) {
            return new CsvToBeanBuilder<TransportRecord>(reader)
                    .withType(TransportRecord.class)
                    .withSkipLines(1) // Skip the header row
                    .withIgnoreLeadingWhiteSpace(true)
                    .build()
                    .parse();
        } catch (Exception e) {
            System.err.println("Error parsing CSV string: " + e.getMessage());
            throw new RuntimeException("Failed to parse CSV string", e);
        }
    }
}
