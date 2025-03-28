package com.example.inventory;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * A simple inventory management system
 */
public class InventoryManager {
    private Map<String, Product> products;
    private List<Transaction> transactions;
    
    public InventoryManager() {
        this.products = new HashMap<>();
        this.transactions = new ArrayList<>();
        System.out.println("InventoryManager initialized");
    }
    
    /**
     * Adds a new product to the inventory.
     */
    public String addProduct(String name, String category, double price, int quantity) {
        if (price < 0 || quantity < 0) {
            throw new IllegalArgumentException("Price and quantity must be positive");
        }
        
        String productId = "P-" + UUID.randomUUID().toString().substring(0, 8);
        Product product = new Product(productId, name, category, price, quantity);
        products.put(productId, product);
        
        // Record transaction
        recordTransaction("STOCK", productId, quantity, "Initial stock");
        
        return productId;
    }
    
    /**
     * Updates product quantity.
     */
    public void updateInventory(String productId, int quantity, String reason) {
        if (!products.containsKey(productId)) {
            throw new IllegalArgumentException("Product not found");
        }
        
        Product product = products.get(productId);
        
        // Check if we have enough inventory for negative quantities
        if (quantity < 0 && product.getQuantity() + quantity < 0) {
            throw new IllegalArgumentException("Insufficient quantity");
        }
        
        // Update the product quantity
        product.setQuantity(product.getQuantity() + quantity);
        
        // Record transaction
        String type = quantity > 0 ? "STOCK" : "SALE";
        recordTransaction(type, productId, Math.abs(quantity), reason);
    }
    
    private void recordTransaction(String type, String productId, int quantity, String reason) {
        String id = "T-" + UUID.randomUUID().toString().substring(0, 8);
        Transaction transaction = new Transaction(id, LocalDate.now(), type, productId, quantity, reason);
        transactions.add(transaction);
    }
    
    public Product getProduct(String productId) {
        return products.get(productId);
    }
    
    public List<Product> getAllProducts() {
        return new ArrayList<>(products.values());
    }
}
