package com.finances_service.model;

import java.math.BigDecimal;

import com.opencsv.bean.CsvBindByPosition;

/**
 * Represents a single financial transaction record.
 * Author: Michael
 */
public class FinancialRecord {
    @CsvBindByPosition(position = 0)
    private String id;
    @CsvBindByPosition(position = 1)
    private String transactionDate;
    @CsvBindByPosition(position = 2)
    private String description;
    @CsvBindByPosition(position = 3)
    private BigDecimal amount;
    @CsvBindByPosition(position = 4)
    private String currency;
    @CsvBindByPosition(position = 5)
    private String category;

    // Basic validation method as per review feedback
    public boolean hasRequiredFields() {
        return id != null && !id.isBlank() &&
               transactionDate != null && !transactionDate.isBlank() &&
               amount != null &&
               currency != null && !currency.isBlank() &&
               category != null && !category.isBlank();
    }

    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    public String getTransactionDate() { return transactionDate; }
    public void setTransactionDate(String transactionDate) { this.transactionDate = transactionDate; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
}
